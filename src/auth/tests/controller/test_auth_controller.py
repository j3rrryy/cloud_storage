from time import time
from unittest.mock import MagicMock, patch

import pytest
from google.protobuf.empty_pb2 import Empty
from google.protobuf.timestamp_pb2 import Timestamp

from enums import ResetCodeStatus
from proto import auth_pb2 as pb2
from settings import Settings

from ..mocks import (
    ACCESS_TOKEN,
    BROWSER,
    CODE,
    CONFIRMATION_TOKEN,
    EMAIL,
    PASSWORD,
    REFRESH_TOKEN,
    SESSION_ID,
    TIMESTAMP,
    USER_AGENT,
    USER_ID,
    USER_IP,
    USERNAME,
)


@pytest.mark.asyncio
@patch("service.auth_service.generate_jwt")
async def test_register(mock_generator, auth_controller):
    mock_generator.return_value = CONFIRMATION_TOKEN
    request = pb2.RegisterRequest(username=USERNAME, email=EMAIL, password=PASSWORD)

    response = await auth_controller.Register(request, MagicMock())

    assert response == pb2.Token(token=CONFIRMATION_TOKEN)


@pytest.mark.asyncio
@patch("service.auth_service.validate_jwt_and_get_user_id")
async def test_confirm_email(mock_validator, auth_controller):
    request = pb2.Token(token=CONFIRMATION_TOKEN)

    response = await auth_controller.ConfirmEmail(request, MagicMock())

    assert response == Empty()


@pytest.mark.asyncio
@patch("service.auth_service.generate_code")
async def test_request_reset_code(mock_generator, auth_controller):
    mock_generator.return_value = CODE
    request = pb2.Email(email=EMAIL)

    response = await auth_controller.RequestResetCode(request, MagicMock())

    assert response == pb2.ResetCodeResponse(
        user_id=USER_ID, username=USERNAME, code=CODE
    )


@pytest.mark.asyncio
async def test_validate_reset_code(cache, auth_controller):
    cache.get.return_value = CODE
    request = pb2.ResetCodeRequest(user_id=USER_ID, code=CODE)

    response = await auth_controller.ValidateResetCode(request, MagicMock())

    assert response == pb2.CodeIsValid(is_valid=True)


@pytest.mark.asyncio
async def test_reset_password(cache, auth_controller):
    cache.get.return_value = ResetCodeStatus.VALIDATED.value
    request = pb2.ResetPasswordRequest(user_id=USER_ID, new_password=PASSWORD)

    response = await auth_controller.ResetPassword(request, MagicMock())

    assert response == Empty()


@pytest.mark.asyncio
@patch("service.auth_service.generate_jwt")
async def test_log_in(mock_generator, auth_controller):
    mock_generator.return_value = ACCESS_TOKEN
    request = pb2.LogInRequest(
        username=USERNAME, password=PASSWORD, user_ip=USER_IP, user_agent=USER_AGENT
    )

    response = await auth_controller.LogIn(request, MagicMock())

    assert response == pb2.LogInResponse(
        access_token=ACCESS_TOKEN,
        refresh_token=ACCESS_TOKEN,
        email=EMAIL,
        browser=BROWSER,
        email_confirmed=False,
    )


@pytest.mark.asyncio
async def test_log_out(auth_controller):
    request = pb2.AccessToken(access_token=ACCESS_TOKEN)

    response = await auth_controller.LogOut(request, MagicMock())

    assert response == Empty()


@pytest.mark.asyncio
@patch("service.auth_service.generate_jwt")
async def test_resend_email_confirmation_mail(mock_generator, auth_controller):
    mock_generator.return_value = CONFIRMATION_TOKEN
    request = pb2.AccessToken(access_token=ACCESS_TOKEN)

    response = await auth_controller.ResendEmailConfirmationMail(request, MagicMock())

    assert response == pb2.EmailConfirmationMail(
        token=CONFIRMATION_TOKEN, username=USERNAME, email=EMAIL
    )


@pytest.mark.asyncio
@patch("service.auth_service.AuthService._cached_access_token")
async def test_auth(mock_cached_access_token, auth_controller):
    mock_cached_access_token.return_value = USER_ID
    request = pb2.AccessToken(access_token=ACCESS_TOKEN)

    response = await auth_controller.Auth(request, MagicMock())

    assert response == pb2.UserId(user_id=USER_ID)


@pytest.mark.asyncio
@patch("service.auth_service.validate_jwt_and_get_user_id")
@patch("service.auth_service.generate_jwt")
async def test_refresh(mock_generator, mock_validator, auth_controller):
    mock_generator.return_value = ACCESS_TOKEN
    request = pb2.RefreshRequest(
        refresh_token=REFRESH_TOKEN, user_ip=USER_IP, user_agent=USER_AGENT
    )

    response = await auth_controller.Refresh(request, MagicMock())

    assert response == pb2.Tokens(access_token=ACCESS_TOKEN, refresh_token=ACCESS_TOKEN)


@pytest.mark.asyncio
@patch("service.auth_service.validate_jwt")
async def test_session_list(mock_validator, cache, auth_controller):
    mock_validator.return_value.exp = 0
    cache.get.return_value = None
    request = pb2.AccessToken(access_token=ACCESS_TOKEN)

    response = await auth_controller.SessionList(request, MagicMock())

    assert response == pb2.Sessions(
        sessions=(
            pb2.SessionInfo(
                session_id=SESSION_ID,
                user_ip=USER_IP,
                browser=BROWSER,
                created_at=Timestamp(seconds=int(TIMESTAMP.timestamp())),
            ),
        )
    )


@pytest.mark.asyncio
async def test_revoke_session(auth_controller):
    request = pb2.RevokeSessionRequest(access_token=ACCESS_TOKEN, session_id=SESSION_ID)

    response = await auth_controller.RevokeSession(request, MagicMock())

    assert response == Empty()


@pytest.mark.asyncio
@patch("service.auth_service.validate_jwt")
async def test_profile(mock_validator, cache, mocked_auth_repository, auth_controller):
    mock_validator.return_value.exp = (
        int(time()) + Settings.MIN_ACCESS_TOKEN_CACHE_TTL + 3
    )
    cache.get.side_effect = [
        None,
        mocked_auth_repository.profile_by_user_id.return_value,
    ]
    request = pb2.AccessToken(access_token=ACCESS_TOKEN)

    response = await auth_controller.Profile(request, MagicMock())

    assert response == pb2.ProfileResponse(
        user_id=USER_ID,
        username=USERNAME,
        email=EMAIL,
        email_confirmed=False,
        registered_at=Timestamp(seconds=int(TIMESTAMP.timestamp())),
    )


@pytest.mark.asyncio
@patch("service.auth_service.generate_jwt")
async def test_update_email(mock_generator, auth_controller):
    mock_generator.return_value = CONFIRMATION_TOKEN
    request = pb2.UpdateEmailRequest(access_token=ACCESS_TOKEN, new_email=EMAIL)

    response = await auth_controller.UpdateEmail(request, MagicMock())

    assert response == pb2.EmailConfirmationMail(
        token=CONFIRMATION_TOKEN, username=USERNAME, email=EMAIL
    )


@pytest.mark.asyncio
async def test_update_password(auth_controller):
    request = pb2.UpdatePasswordRequest(
        access_token=ACCESS_TOKEN, old_password=PASSWORD, new_password=PASSWORD
    )

    response = await auth_controller.UpdatePassword(request, MagicMock())

    assert response == Empty()


@pytest.mark.asyncio
@patch("service.auth_service.AuthService._cached_access_token")
async def test_delete_profile(mock_cached_access_token, auth_controller):
    mock_cached_access_token.return_value = USER_ID
    request = pb2.AccessToken(access_token=ACCESS_TOKEN)

    response = await auth_controller.DeleteProfile(request, MagicMock())

    assert response == pb2.UserId(user_id=USER_ID)
