from unittest.mock import MagicMock, patch

import pytest
from google.protobuf.empty_pb2 import Empty
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import ServicerContext

from proto import auth_pb2 as pb2

from .mocks import (
    ACCESS_TOKEN,
    BROWSER,
    CODE,
    EMAIL,
    PASSWORD,
    REFRESH_TOKEN,
    SESSION_ID,
    TIMESTAMP,
    USER_AGENT,
    USER_ID,
    USER_IP,
    USERNAME,
    VERIFICATION_TOKEN,
    create_cache,
    create_repository,
)


@pytest.mark.asyncio
async def test_register(auth_controller):
    with (
        patch("service.auth.AuthRepository", new_callable=create_repository),
        patch("service.auth.generate_jwt") as mock_generator,
    ):
        mock_generator.return_value = VERIFICATION_TOKEN
        request = pb2.RegisterRequest(username=USERNAME, email=EMAIL, password=PASSWORD)
        response = await auth_controller.Register(request, MagicMock(ServicerContext))
        assert response == pb2.VerificationMail(
            verification_token=VERIFICATION_TOKEN, username=USERNAME, email=EMAIL
        )


@pytest.mark.asyncio
async def test_verify_email(auth_controller):
    with (
        patch("service.auth.AuthRepository", new_callable=create_repository),
        patch("service.auth.cache", new_callable=create_cache),
        patch("service.auth.validate_jwt"),
    ):
        request = pb2.VerificationToken(verification_token=VERIFICATION_TOKEN)
        response = await auth_controller.VerifyEmail(
            request, MagicMock(ServicerContext)
        )
        assert response == Empty()


@pytest.mark.asyncio
async def test_request_reset_code(auth_controller):
    with (
        patch("service.auth.AuthRepository", new_callable=create_repository),
        patch("service.auth.cache", new_callable=create_cache),
        patch("service.auth.generate_reset_code") as mock_generator,
    ):
        mock_generator.return_value = CODE
        request = pb2.Email(email=EMAIL)
        response = await auth_controller.RequestResetCode(
            request, MagicMock(ServicerContext)
        )
        assert response == pb2.ResetCodeResponse(
            user_id=USER_ID, username=USERNAME, code=CODE
        )


@pytest.mark.asyncio
async def test_validate_reset_code(auth_controller):
    with patch("service.auth.cache", new_callable=create_cache) as mock_cache:
        mock_cache.get.return_value = CODE
        request = pb2.ResetCodeRequest(user_id=USER_ID, code=CODE)
        response = await auth_controller.ValidateResetCode(
            request, MagicMock(ServicerContext)
        )
        assert response == pb2.CodeIsValid(is_valid=True)


@pytest.mark.asyncio
async def test_reset_password(auth_controller):
    with (
        patch("service.auth.AuthRepository", new_callable=create_repository),
        patch("service.auth.cache", new_callable=create_cache) as mock_cache,
    ):
        mock_cache.get.return_value = "validated"
        request = pb2.ResetPasswordRequest(user_id=USER_ID, new_password=PASSWORD)
        response = await auth_controller.ResetPassword(
            request, MagicMock(ServicerContext)
        )
        assert response == Empty()


@pytest.mark.asyncio
async def test_log_in(auth_controller):
    with (
        patch("service.auth.AuthRepository", new_callable=create_repository),
        patch("service.auth.cache", new_callable=create_cache),
        patch("service.auth.generate_jwt") as mock_generator,
    ):
        mock_generator.return_value = ACCESS_TOKEN
        request = pb2.LogInRequest(
            username=USERNAME, password=PASSWORD, user_ip=USER_IP, user_agent=USER_AGENT
        )
        response = await auth_controller.LogIn(request, MagicMock(ServicerContext))
        assert response == pb2.LogInResponse(
            access_token=ACCESS_TOKEN,
            refresh_token=ACCESS_TOKEN,
            email=EMAIL,
            browser=BROWSER,
            verified=True,
        )


@pytest.mark.asyncio
async def test_log_out(auth_controller):
    with (
        patch("service.auth.AuthRepository", new_callable=create_repository),
        patch("service.auth.cache", new_callable=create_cache),
        patch("service.auth.validate_jwt"),
    ):
        request = pb2.AccessToken(access_token=ACCESS_TOKEN)
        response = await auth_controller.LogOut(request, MagicMock(ServicerContext))
        assert response == Empty()


@pytest.mark.asyncio
async def test_resend_verification_mail(auth_controller):
    with (
        patch("service.auth.AuthRepository", new_callable=create_repository),
        patch("service.auth.validate_jwt"),
        patch("service.auth.generate_jwt") as mock_generator,
    ):
        mock_generator.return_value = VERIFICATION_TOKEN
        request = pb2.AccessToken(access_token=ACCESS_TOKEN)
        response = await auth_controller.ResendVerificationMail(
            request, MagicMock(ServicerContext)
        )
        assert response == pb2.VerificationMail(
            verification_token=VERIFICATION_TOKEN, username=USERNAME, email=EMAIL
        )


@pytest.mark.asyncio
async def test_auth(auth_controller):
    with (
        patch("service.auth.AuthRepository", new_callable=create_repository),
        patch("service.auth.cache", new_callable=create_cache),
        patch("service.auth.validate_jwt") as mock_validator,
    ):
        mock_validator.return_value = USER_ID
        request = pb2.AccessToken(access_token=ACCESS_TOKEN)
        response = await auth_controller.Auth(request, MagicMock(ServicerContext))
        assert response == pb2.UserId(user_id=USER_ID)


@pytest.mark.asyncio
async def test_refresh(auth_controller):
    with (
        patch("service.auth.AuthRepository", new_callable=create_repository),
        patch("service.auth.cache", new_callable=create_cache),
        patch("service.auth.validate_jwt"),
        patch("service.auth.generate_jwt") as mock_generator,
    ):
        mock_generator.return_value = ACCESS_TOKEN
        request = pb2.RefreshRequest(
            refresh_token=REFRESH_TOKEN, user_ip=USER_IP, user_agent=USER_AGENT
        )
        response = await auth_controller.Refresh(request, MagicMock(ServicerContext))
        assert response == pb2.Tokens(
            access_token=ACCESS_TOKEN, refresh_token=ACCESS_TOKEN
        )


@pytest.mark.asyncio
async def test_session_list(auth_controller):
    with (
        patch("service.auth.AuthRepository", new_callable=create_repository),
        patch("service.auth.cache", new_callable=create_cache),
        patch("service.auth.validate_jwt"),
    ):
        request = pb2.AccessToken(access_token=ACCESS_TOKEN)
        response = await auth_controller.SessionList(
            request, MagicMock(ServicerContext)
        )
        assert response == pb2.Sessions(
            sessions=(
                pb2.SessionInfo(
                    session_id=SESSION_ID,
                    user_ip=USER_IP,
                    browser=BROWSER,
                    last_accessed=Timestamp(seconds=int(TIMESTAMP.timestamp())),
                ),
            )
        )


@pytest.mark.asyncio
async def test_revoke_session(auth_controller):
    with (
        patch("service.auth.AuthRepository", new_callable=create_repository),
        patch("service.auth.cache", new_callable=create_cache),
        patch("service.auth.validate_jwt"),
    ):
        request = pb2.RevokeSessionRequest(
            access_token=ACCESS_TOKEN, session_id=SESSION_ID
        )
        response = await auth_controller.RevokeSession(
            request, MagicMock(ServicerContext)
        )
        assert response == Empty()


@pytest.mark.asyncio
async def test_profile(auth_controller):
    with (
        patch("service.auth.AuthRepository", new_callable=create_repository),
        patch("service.auth.cache", new_callable=create_cache),
        patch("service.auth.validate_jwt"),
    ):
        request = pb2.AccessToken(access_token=ACCESS_TOKEN)
        response = await auth_controller.Profile(request, MagicMock(ServicerContext))
        assert response == pb2.ProfileResponse(
            user_id=USER_ID,
            username=USERNAME,
            email=EMAIL,
            verified=True,
            registered=Timestamp(seconds=int(TIMESTAMP.timestamp())),
        )


@pytest.mark.asyncio
async def test_update_email(auth_controller):
    with (
        patch("service.auth.AuthRepository", new_callable=create_repository),
        patch("service.auth.cache", new_callable=create_cache),
        patch("service.auth.validate_jwt"),
        patch("service.auth.generate_jwt") as mock_generator,
    ):
        mock_generator.return_value = VERIFICATION_TOKEN
        request = pb2.UpdateEmailRequest(access_token=ACCESS_TOKEN, new_email=EMAIL)
        response = await auth_controller.UpdateEmail(
            request, MagicMock(ServicerContext)
        )
        assert response == pb2.VerificationMail(
            verification_token=VERIFICATION_TOKEN, username=USERNAME, email=EMAIL
        )


@pytest.mark.asyncio
async def test_update_password(auth_controller):
    with (
        patch("service.auth.AuthRepository", new_callable=create_repository),
        patch("service.auth.validate_jwt"),
    ):
        request = pb2.UpdatePasswordRequest(
            access_token=ACCESS_TOKEN, old_password=PASSWORD, new_password=PASSWORD
        )
        response = await auth_controller.UpdatePassword(
            request, MagicMock(ServicerContext)
        )
        assert response == Empty()


@pytest.mark.asyncio
async def test_delete_profile(auth_controller):
    with (
        patch("service.auth.AuthRepository", new_callable=create_repository),
        patch("service.auth.cache", new_callable=create_cache),
        patch("service.auth.validate_jwt") as mock_validator,
    ):
        mock_validator.return_value = USER_ID
        request = pb2.AccessToken(access_token=ACCESS_TOKEN)
        response = await auth_controller.DeleteProfile(
            request, MagicMock(ServicerContext)
        )
        assert response == pb2.UserId(user_id=USER_ID)
