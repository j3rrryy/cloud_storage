from datetime import timedelta

import pytest
from grpc import StatusCode
from jwskate import Jwt, SignedJwt

from enums import TokenType
from exceptions import BaseAppException
from security import (
    PRIVATE_KEY,
    PUBLIC_KEY,
    compare_passwords,
    generate_code,
    generate_jwt,
    get_jwt_hash,
    get_password_hash,
    validate_jwt,
    validate_jwt_and_get_user_id,
)
from settings import Settings
from utils import utc_now_aware

from ..mocks import ACCESS_TOKEN, PASSWORD, USER_ID


@pytest.mark.parametrize(
    "token_type", [TokenType.ACCESS, TokenType.REFRESH, TokenType.EMAIL_CONFIRMATION]
)
def test_generate_jwt(token_type):
    now = utc_now_aware()

    token = generate_jwt(USER_ID, token_type)

    jwt = Jwt(token)
    assert isinstance(token, str)
    assert isinstance(jwt, SignedJwt)
    assert jwt.verify_signature(PUBLIC_KEY, "EdDSA")
    assert jwt.issuer == Settings.APP_NAME
    assert jwt.expires_at is not None
    assert jwt.subject is not None
    match token_type:
        case TokenType.ACCESS:
            assert jwt.expires_at <= now + timedelta(minutes=15)
        case TokenType.REFRESH:
            assert jwt.expires_at <= now + timedelta(days=30)
        case TokenType.EMAIL_CONFIRMATION:
            assert jwt.expires_at <= now + timedelta(days=3)


@pytest.mark.parametrize(
    "token_type", [TokenType.ACCESS, TokenType.REFRESH, TokenType.EMAIL_CONFIRMATION]
)
def test_validate_jwt(token_type):
    token = generate_jwt(USER_ID, token_type)

    jwt = validate_jwt(token, token_type)

    assert jwt.subject == USER_ID


def test_validate_jwt_broken_token():
    with pytest.raises(BaseAppException) as exc_info:
        validate_jwt("broken_token", TokenType.ACCESS)

    assert exc_info.value.status_code == StatusCode.UNAUTHENTICATED
    assert exc_info.value.details == "Token is invalid"


@pytest.mark.parametrize(
    "modified, in_token_type, out_token_type, expected_message",
    [
        (
            {"iss": "wrong_issuer"},
            TokenType.ACCESS,
            TokenType.ACCESS,
            "Token is invalid",
        ),
        ({"sub": None}, TokenType.ACCESS, TokenType.ACCESS, "Token is invalid"),
        ({}, TokenType.ACCESS, None, "Token is invalid"),
        ({}, TokenType.ACCESS, TokenType.REFRESH, "Invalid token type"),
        (
            {"exp": utc_now_aware()},
            TokenType.ACCESS,
            TokenType.ACCESS,
            "Refresh the tokens",
        ),
        ({"exp": utc_now_aware()}, TokenType.REFRESH, TokenType.REFRESH, "Re-log in"),
        (
            {"exp": utc_now_aware()},
            TokenType.EMAIL_CONFIRMATION,
            TokenType.EMAIL_CONFIRMATION,
            "Resend the email confirmation mail",
        ),
    ],
)
def test_validate_jwt_exceptions(
    modified, in_token_type, out_token_type, expected_message
):
    jwt = Jwt(generate_jwt(USER_ID, in_token_type))
    claims = jwt.claims  # type: ignore
    typ = str(out_token_type.value) if out_token_type else None
    claims.update(modified)
    new_token = str(Jwt.sign(claims, PRIVATE_KEY, alg="EdDSA", typ=typ))

    with pytest.raises(BaseAppException) as exc_info:
        validate_jwt(new_token, in_token_type)

    assert exc_info.value.status_code == StatusCode.UNAUTHENTICATED
    assert exc_info.value.details == expected_message


@pytest.mark.parametrize(
    "token_type", [TokenType.ACCESS, TokenType.REFRESH, TokenType.EMAIL_CONFIRMATION]
)
def test_validate_jwt_and_get_user_id(token_type):
    token = generate_jwt(USER_ID, token_type)

    user_id = validate_jwt_and_get_user_id(token, token_type)

    assert user_id == USER_ID


def test_get_jwt_hash():
    hashed_jwt = get_jwt_hash(ACCESS_TOKEN)

    assert hashed_jwt != ACCESS_TOKEN


def test_get_password_hash():
    hashed_password = get_password_hash(PASSWORD)

    assert hashed_password != PASSWORD


def test_compare_passwords():
    hashed_password = get_password_hash(PASSWORD)

    compare_passwords(hashed_password, PASSWORD)


def test_compare_passwords_exception():
    hashed_password = get_password_hash(PASSWORD)

    with pytest.raises(BaseAppException) as exc_info:
        compare_passwords(hashed_password, PASSWORD + "0")

    assert exc_info.value.status_code == StatusCode.UNAUTHENTICATED
    assert exc_info.value.details == "Invalid credentials"


def test_generate_code():
    code = generate_code()

    assert code.isdigit()
    assert len(code) == 6
