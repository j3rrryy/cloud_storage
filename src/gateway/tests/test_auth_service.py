import pytest

from dto import auth as auth_dto
from services import Auth

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
)


@pytest.mark.asyncio
async def test_register(auth_service: Auth):
    dto = auth_dto.RegistrationDTO(USERNAME, EMAIL, PASSWORD)
    response = await auth_service.register(dto)
    assert response.verification_token == VERIFICATION_TOKEN
    assert response.username == USERNAME
    assert response.email == EMAIL


@pytest.mark.asyncio
async def test_verify_email(auth_service: Auth):
    response = await auth_service.verify_email(VERIFICATION_TOKEN)
    assert response is None


@pytest.mark.asyncio
async def test_request_reset_code(auth_service: Auth):
    response = await auth_service.request_reset_code(EMAIL)
    assert response.user_id == USER_ID
    assert response.username == USERNAME
    assert response.code == CODE


@pytest.mark.asyncio
async def test_validate_reset_code(auth_service: Auth):
    dto = auth_dto.ResetCodeDTO(USER_ID, CODE)
    response = await auth_service.validate_code(dto)
    assert response


@pytest.mark.asyncio
async def test_reset_password(auth_service: Auth):
    dto = auth_dto.ResetPasswordDTO(USER_ID, PASSWORD)
    response = await auth_service.reset_password(dto)
    assert response is None


@pytest.mark.asyncio
async def test_log_in(auth_service: Auth):
    dto = auth_dto.LogInDTO(USERNAME, PASSWORD, USER_IP, USER_AGENT)
    response = await auth_service.log_in(dto)
    assert response.access_token == ACCESS_TOKEN
    assert response.refresh_token == REFRESH_TOKEN
    assert response.email == EMAIL
    assert response.browser == BROWSER
    assert response.verified


@pytest.mark.asyncio
async def test_log_out(auth_service: Auth):
    response = await auth_service.log_out(ACCESS_TOKEN)
    assert response is None


@pytest.mark.asyncio
async def test_resend_verification_mail(auth_service: Auth):
    response = await auth_service.resend_verification_mail(ACCESS_TOKEN)
    assert response.verification_token == VERIFICATION_TOKEN
    assert response.username == USERNAME
    assert response.email == EMAIL


@pytest.mark.asyncio
async def test_auth(auth_service: Auth):
    response = await auth_service.auth(ACCESS_TOKEN)
    assert response.user_id == USER_ID
    assert response.verified


@pytest.mark.asyncio
async def test_refresh(auth_service: Auth):
    dto = auth_dto.RefreshDTO(REFRESH_TOKEN, USER_IP, USER_AGENT)
    response = await auth_service.refresh(dto)
    assert response.access_token == ACCESS_TOKEN
    assert response.refresh_token == REFRESH_TOKEN


@pytest.mark.asyncio
async def test_session_list(auth_service: Auth):
    response = await auth_service.session_list(ACCESS_TOKEN)
    first_session = next(response)
    assert first_session.session_id == SESSION_ID
    assert first_session.user_ip == USER_IP
    assert first_session.browser == BROWSER
    assert first_session.last_accessed == TIMESTAMP


@pytest.mark.asyncio
async def test_revoke_session(auth_service: Auth):
    dto = auth_dto.RevokeSessionDTO(ACCESS_TOKEN, SESSION_ID)
    response = await auth_service.revoke_session(dto)
    assert response is None


@pytest.mark.asyncio
async def test_profile(auth_service: Auth):
    response = await auth_service.profile(ACCESS_TOKEN)
    assert response.user_id == USER_ID
    assert response.username == USERNAME
    assert response.email == EMAIL
    assert response.verified
    assert response.registered == TIMESTAMP


@pytest.mark.asyncio
async def test_update_email(auth_service: Auth):
    dto = auth_dto.UpdateEmailDTO(ACCESS_TOKEN, EMAIL)
    response = await auth_service.update_email(dto)
    assert response.verification_token == VERIFICATION_TOKEN
    assert response.username == USERNAME
    assert response.email == EMAIL


@pytest.mark.asyncio
async def test_update_password(auth_service: Auth):
    dto = auth_dto.UpdatePasswordDTO(ACCESS_TOKEN, PASSWORD, PASSWORD)
    response = await auth_service.update_password(dto)
    assert response is None


@pytest.mark.asyncio
async def test_delete_profile(auth_service: Auth):
    response = await auth_service.delete_profile(ACCESS_TOKEN)
    assert response == USER_ID
