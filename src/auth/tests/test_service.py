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
    create_database_crud,
)


@pytest.mark.asyncio
async def test_register(auth_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.generate_jwt") as mock_generator,
    ):
        mock_generator.return_value = VERIFICATION_TOKEN
        request = pb2.RegisterRequest(username=USERNAME, email=EMAIL, password=PASSWORD)
        response = await auth_servicer.Register(request, MagicMock(ServicerContext))
        assert response == pb2.VerificationMail(
            verification_token=VERIFICATION_TOKEN, username=USERNAME, email=EMAIL
        )


@pytest.mark.asyncio
async def test_verify_email(auth_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.cache", new_callable=create_cache),
        patch("controllers.database.validate_jwt"),
    ):
        request = pb2.VerificationToken(verification_token=VERIFICATION_TOKEN)
        response = await auth_servicer.VerifyEmail(request, MagicMock(ServicerContext))
        assert response == Empty()


@pytest.mark.asyncio
async def test_request_reset_code(auth_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.cache", new_callable=create_cache),
        patch("controllers.database.generate_reset_code") as mock_generator,
    ):
        mock_generator.return_value = CODE
        request = pb2.Email(email=EMAIL)
        response = await auth_servicer.RequestResetCode(
            request, MagicMock(ServicerContext)
        )
        assert response == pb2.ResetCodeResponse(
            user_id=USER_ID, username=USERNAME, code=CODE
        )


@pytest.mark.asyncio
async def test_validate_reset_code(auth_servicer):
    with patch("controllers.database.cache", new_callable=create_cache) as mock_cache:
        mock_cache.get.return_value = CODE
        request = pb2.ResetCodeRequest(user_id=USER_ID, code=CODE)
        response = await auth_servicer.ValidateResetCode(
            request, MagicMock(ServicerContext)
        )
        assert response == pb2.CodeIsValid(is_valid=True)


@pytest.mark.asyncio
async def test_reset_password(auth_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.cache", new_callable=create_cache) as mock_cache,
    ):
        mock_cache.get.return_value = "validated"
        request = pb2.ResetPasswordRequest(user_id=USER_ID, new_password=PASSWORD)
        response = await auth_servicer.ResetPassword(
            request, MagicMock(ServicerContext)
        )
        assert response == Empty()


@pytest.mark.asyncio
async def test_log_in(auth_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.cache", new_callable=create_cache),
        patch("controllers.database.generate_jwt") as mock_generator,
    ):
        mock_generator.return_value = ACCESS_TOKEN
        request = pb2.LogInRequest(
            username=USERNAME, password=PASSWORD, user_ip=USER_IP, user_agent=USER_AGENT
        )
        response = await auth_servicer.LogIn(request, MagicMock(ServicerContext))
        assert response == pb2.LogInResponse(
            access_token=ACCESS_TOKEN,
            refresh_token=ACCESS_TOKEN,
            email=EMAIL,
            browser=BROWSER,
            verified=True,
        )


@pytest.mark.asyncio
async def test_log_out(auth_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.cache", new_callable=create_cache),
        patch("controllers.database.validate_jwt"),
    ):
        request = pb2.AccessToken(access_token=ACCESS_TOKEN)
        response = await auth_servicer.LogOut(request, MagicMock(ServicerContext))
        assert response == Empty()


@pytest.mark.asyncio
async def test_resend_verification_mail(auth_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.validate_jwt"),
        patch("controllers.database.generate_jwt") as mock_generator,
    ):
        mock_generator.return_value = VERIFICATION_TOKEN
        request = pb2.AccessToken(access_token=ACCESS_TOKEN)
        response = await auth_servicer.ResendVerificationMail(
            request, MagicMock(ServicerContext)
        )
        assert response == pb2.VerificationMail(
            verification_token=VERIFICATION_TOKEN, username=USERNAME, email=EMAIL
        )


@pytest.mark.asyncio
async def test_auth(auth_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.cache", new_callable=create_cache),
        patch("controllers.database.validate_jwt") as mock_validator,
    ):
        mock_validator.return_value = USER_ID
        request = pb2.AccessToken(access_token=ACCESS_TOKEN)
        response = await auth_servicer.Auth(request, MagicMock(ServicerContext))
        assert response == pb2.AuthResponse(user_id=USER_ID, verified=True)


@pytest.mark.asyncio
async def test_refresh(auth_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.cache", new_callable=create_cache),
        patch("controllers.database.validate_jwt"),
        patch("controllers.database.generate_jwt") as mock_generator,
    ):
        mock_generator.return_value = ACCESS_TOKEN
        request = pb2.RefreshRequest(
            refresh_token=REFRESH_TOKEN, user_ip=USER_IP, user_agent=USER_AGENT
        )
        response = await auth_servicer.Refresh(request, MagicMock(ServicerContext))
        assert response == pb2.Tokens(
            access_token=ACCESS_TOKEN, refresh_token=ACCESS_TOKEN
        )


@pytest.mark.asyncio
async def test_session_list(auth_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.cache", new_callable=create_cache),
        patch("controllers.database.validate_jwt"),
    ):
        request = pb2.AccessToken(access_token=ACCESS_TOKEN)
        response = await auth_servicer.SessionList(request, MagicMock(ServicerContext))
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
async def test_revoke_session(auth_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.cache", new_callable=create_cache),
        patch("controllers.database.validate_jwt"),
    ):
        request = pb2.RevokeSessionRequest(
            access_token=ACCESS_TOKEN, session_id=SESSION_ID
        )
        response = await auth_servicer.RevokeSession(
            request, MagicMock(ServicerContext)
        )
        assert response == Empty()


@pytest.mark.asyncio
async def test_profile(auth_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.cache", new_callable=create_cache),
        patch("controllers.database.validate_jwt"),
    ):
        request = pb2.AccessToken(access_token=ACCESS_TOKEN)
        response = await auth_servicer.Profile(request, MagicMock(ServicerContext))
        assert response == pb2.ProfileResponse(
            user_id=USER_ID,
            username=USERNAME,
            email=EMAIL,
            verified=True,
            registered=Timestamp(seconds=int(TIMESTAMP.timestamp())),
        )


@pytest.mark.asyncio
async def test_update_email(auth_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.cache", new_callable=create_cache),
        patch("controllers.database.validate_jwt"),
        patch("controllers.database.generate_jwt") as mock_generator,
    ):
        mock_generator.return_value = VERIFICATION_TOKEN
        request = pb2.UpdateEmailRequest(access_token=ACCESS_TOKEN, new_email=EMAIL)
        response = await auth_servicer.UpdateEmail(request, MagicMock(ServicerContext))
        assert response == pb2.VerificationMail(
            verification_token=VERIFICATION_TOKEN, username=USERNAME, email=EMAIL
        )


@pytest.mark.asyncio
async def test_update_password(auth_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.validate_jwt"),
    ):
        request = pb2.UpdatePasswordRequest(
            access_token=ACCESS_TOKEN, old_password=PASSWORD, new_password=PASSWORD
        )
        response = await auth_servicer.UpdatePassword(
            request, MagicMock(ServicerContext)
        )
        assert response == Empty()


@pytest.mark.asyncio
async def test_delete_profile(auth_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.cache", new_callable=create_cache),
        patch("controllers.database.validate_jwt") as mock_validator,
    ):
        mock_validator.return_value = USER_ID
        request = pb2.AccessToken(access_token=ACCESS_TOKEN)
        response = await auth_servicer.DeleteProfile(
            request, MagicMock(ServicerContext)
        )
        assert response == pb2.UserId(user_id=USER_ID)
