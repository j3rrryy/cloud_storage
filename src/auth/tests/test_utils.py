import os
from datetime import datetime as dt
from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from grpc import StatusCode
from jwskate import Jwt, SignedJwt

from enums import TokenTypes
from exceptions import UnauthenticatedException
from utils import (
    ExceptionHandler,
    compare_passwords,
    convert_user_agent,
    generate_jwt,
    generate_reset_code,
    get_hashed_password,
    validate_jwt,
    validate_jwt_and_get_user_id,
)

from .mocks import PASSWORD, USER_ID


@pytest.mark.asyncio
@patch("utils.utils.logger")
async def test_exception_handler_success(mock_logger):
    context = AsyncMock()

    async def mock_func():
        return "ok"

    res = await ExceptionHandler.handle(context, mock_func)

    assert res == "ok"
    mock_logger.error.assert_not_called()
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
    mock_logger.error.assert_called_once_with(
        "Status code: UNKNOWN (2), details: Test details"
    )
    context.abort.assert_awaited_once_with(StatusCode.UNKNOWN, "Test details")


def test_generate_reset_code():
    code = generate_reset_code()
    assert isinstance(code, str)
    assert code.isdigit()
    assert len(code) == 6


@pytest.mark.parametrize(
    "token_type", [TokenTypes.ACCESS, TokenTypes.REFRESH, TokenTypes.VERIFICATION]
)
def test_generate_jwt(token_type, mock_key_pair):
    token = generate_jwt(USER_ID, token_type)  # type: ignore
    jwt = Jwt(token)

    assert isinstance(token, str)
    assert isinstance(jwt, SignedJwt)
    assert jwt.verify_signature(mock_key_pair.public_key, "EdDSA")
    assert jwt.issuer == os.environ["APP_NAME"]
    assert jwt.expires_at is not None
    assert jwt.subject is not None

    exp = jwt.expires_at.replace(tzinfo=None)

    match token_type:
        case TokenTypes.ACCESS:
            assert exp <= dt.now() + timedelta(minutes=15)
        case TokenTypes.REFRESH:
            assert exp <= dt.now() + timedelta(days=30)
        case TokenTypes.VERIFICATION:
            assert exp <= dt.now() + timedelta(days=3)


@pytest.mark.parametrize(
    "token_type", [TokenTypes.ACCESS, TokenTypes.REFRESH, TokenTypes.VERIFICATION]
)
def test_validate_jwt(token_type, mock_key_pair):
    token = generate_jwt(USER_ID, token_type)  # type: ignore
    jwt = validate_jwt(token, token_type)  # type: ignore
    assert jwt.subject == USER_ID


def test_validate_broken_jwt(mock_key_pair):
    with pytest.raises(UnauthenticatedException) as exc_info:
        validate_jwt("broken_token", TokenTypes.ACCESS)  # type: ignore

    assert exc_info.value.args == (StatusCode.UNAUTHENTICATED, "Token is invalid")


@pytest.mark.parametrize(
    "token_type", [TokenTypes.ACCESS, TokenTypes.REFRESH, TokenTypes.VERIFICATION]
)
def test_validate_jwt_and_get_user_id(token_type, mock_key_pair):
    token = generate_jwt(USER_ID, token_type)  # type: ignore
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
        ({"exp": dt.now()}, TokenTypes.ACCESS, TokenTypes.ACCESS, "Refresh the tokens"),
        ({"exp": dt.now()}, TokenTypes.REFRESH, TokenTypes.REFRESH, "Re-log in"),
        (
            {"exp": dt.now()},
            TokenTypes.VERIFICATION,
            TokenTypes.VERIFICATION,
            "Resend the verification mail",
        ),
    ],
)
def test_validate_jwt_exceptions(
    modified, in_token_type, out_token_type, expected_message, mock_key_pair
):
    token = generate_jwt(USER_ID, in_token_type)  # type: ignore
    jwt = Jwt(token)

    claims = jwt.claims  # type: ignore
    typ = str(out_token_type.value) if out_token_type else None
    claims.update(modified)

    new_token = str(Jwt.sign(claims, mock_key_pair.private_key, alg="EdDSA", typ=typ))
    with pytest.raises(UnauthenticatedException) as exc_info:
        validate_jwt(new_token, in_token_type)  # type: ignore

    assert exc_info.value.args == (StatusCode.UNAUTHENTICATED, expected_message)


def test_compare_passwords():
    hashed_password = get_hashed_password(PASSWORD)
    compare_passwords(PASSWORD, hashed_password)


def test_compare_exception():
    hashed_password = get_hashed_password(PASSWORD)
    with pytest.raises(UnauthenticatedException) as exc_info:
        compare_passwords(PASSWORD + "0", hashed_password)

    assert exc_info.value.args == (StatusCode.UNAUTHENTICATED, "Invalid credentials")


def test_get_hashed_password():
    hashed_password = get_hashed_password(PASSWORD)
    assert hashed_password != PASSWORD


def test_convert_user_agent():
    user_agent = convert_user_agent(
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
    )
    assert user_agent == "Firefox 47.0, Windows 7"
