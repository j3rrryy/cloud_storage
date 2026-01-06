from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from grpc import StatusCode
from jwskate import Jwt, SignedJwt

from enums import TokenTypes
from exceptions import UnauthenticatedException
from settings import Settings
from utils import (
    ExceptionHandler,
    compare_passwords,
    generate_code,
    generate_jwt,
    get_jwt_hash,
    get_password_hash,
    utc_now_naive,
    validate_jwt,
    validate_jwt_and_get_user_id,
)

from .mocks import ACCESS_TOKEN, PASSWORD, USER_ID


@pytest.mark.asyncio
@patch("utils.utils.logger")
async def test_exception_handler_success(mock_logger):
    context = AsyncMock()

    async def mock_func():
        return "ok"

    res = await ExceptionHandler.handle(context, mock_func)

    assert res == "ok"
    mock_logger.info.assert_not_called()
    context.abort.assert_not_called()


@pytest.mark.asyncio
@patch("utils.utils.logger")
async def test_exception_handler_exception(mock_logger):
    context = AsyncMock()

    async def mock_func():
        raise Exception(StatusCode.UNKNOWN, "Test details")

    with pytest.raises(Exception) as exc_info:
        await ExceptionHandler.handle(context, mock_func)

    assert exc_info.value.args == (StatusCode.UNKNOWN, "Test details")
    mock_logger.info.assert_called_once_with(
        "Status code: UNKNOWN (2), details: Test details"
    )
    context.abort.assert_awaited_once_with(StatusCode.UNKNOWN, "Test details")


def test_utc_now_naive():
    now = utc_now_naive()

    assert isinstance(now, datetime)
    assert now.tzinfo is None


def test_generate_code():
    code = generate_code()

    assert isinstance(code, str)
    assert code.isdigit()
    assert len(code) == 6


@pytest.mark.parametrize(
    "token_type", [TokenTypes.ACCESS, TokenTypes.REFRESH, TokenTypes.EMAIL_CONFIRMATION]
)
def test_generate_jwt(token_type, mock_key_pair):
    now = utc_now_naive()

    token = generate_jwt(USER_ID, token_type)

    jwt = Jwt(token)
    assert isinstance(token, str)
    assert isinstance(jwt, SignedJwt)
    assert jwt.verify_signature(mock_key_pair.public_key, "EdDSA")
    assert jwt.issuer == Settings.APP_NAME
    assert jwt.expires_at is not None
    assert jwt.subject is not None
    exp = jwt.expires_at.replace(tzinfo=None)
    match token_type:
        case TokenTypes.ACCESS:
            assert exp <= now + timedelta(minutes=15)
        case TokenTypes.REFRESH:
            assert exp <= now + timedelta(days=30)
        case TokenTypes.EMAIL_CONFIRMATION:
            assert exp <= now + timedelta(days=3)


@pytest.mark.parametrize(
    "token_type", [TokenTypes.ACCESS, TokenTypes.REFRESH, TokenTypes.EMAIL_CONFIRMATION]
)
def test_validate_jwt(token_type, mock_key_pair):
    token = generate_jwt(USER_ID, token_type)

    jwt = validate_jwt(token, token_type)

    assert jwt.subject == USER_ID


def test_validate_broken_jwt(mock_key_pair):
    with pytest.raises(UnauthenticatedException) as exc_info:
        validate_jwt("broken_token", TokenTypes.ACCESS)

    assert exc_info.value.args == (StatusCode.UNAUTHENTICATED, "Token is invalid")


@pytest.mark.parametrize(
    "token_type", [TokenTypes.ACCESS, TokenTypes.REFRESH, TokenTypes.EMAIL_CONFIRMATION]
)
def test_validate_jwt_and_get_user_id(token_type, mock_key_pair):
    token = generate_jwt(USER_ID, token_type)

    user_id = validate_jwt_and_get_user_id(token, token_type)

    assert user_id == USER_ID


@pytest.mark.parametrize(
    "modified, in_token_type, out_token_type, expected_message",
    [
        (
            {"iss": "wrong_issuer"},
            TokenTypes.ACCESS,
            TokenTypes.ACCESS,
            "Token is invalid",
        ),
        ({"sub": None}, TokenTypes.ACCESS, TokenTypes.ACCESS, "Token is invalid"),
        ({}, TokenTypes.ACCESS, None, "Token is invalid"),
        ({}, TokenTypes.ACCESS, TokenTypes.REFRESH, "Invalid token type"),
        (
            {"exp": utc_now_naive()},
            TokenTypes.ACCESS,
            TokenTypes.ACCESS,
            "Refresh the tokens",
        ),
        ({"exp": utc_now_naive()}, TokenTypes.REFRESH, TokenTypes.REFRESH, "Re-log in"),
        (
            {"exp": utc_now_naive()},
            TokenTypes.EMAIL_CONFIRMATION,
            TokenTypes.EMAIL_CONFIRMATION,
            "Resend the email confirmation mail",
        ),
    ],
)
def test_validate_jwt_exceptions(
    modified, in_token_type, out_token_type, expected_message, mock_key_pair
):
    jwt = Jwt(generate_jwt(USER_ID, in_token_type))
    claims = jwt.claims
    typ = str(out_token_type.value) if out_token_type else None
    claims.update(modified)
    new_token = str(Jwt.sign(claims, mock_key_pair.private_key, alg="EdDSA", typ=typ))

    with pytest.raises(UnauthenticatedException) as exc_info:
        validate_jwt(new_token, in_token_type)

    assert exc_info.value.args == (StatusCode.UNAUTHENTICATED, expected_message)


def test_get_hashed_password():
    hashed_password = get_password_hash(PASSWORD)

    assert hashed_password != PASSWORD


def test_compare_passwords():
    hashed_password = get_password_hash(PASSWORD)

    compare_passwords(PASSWORD, hashed_password)


def test_compare_exception():
    hashed_password = get_password_hash(PASSWORD)

    with pytest.raises(UnauthenticatedException) as exc_info:
        compare_passwords(PASSWORD + "0", hashed_password)

    assert exc_info.value.args == (StatusCode.UNAUTHENTICATED, "Invalid credentials")


def test_get_hashed_jwt():
    hashed_jwt = get_jwt_hash(ACCESS_TOKEN)

    assert hashed_jwt != ACCESS_TOKEN
