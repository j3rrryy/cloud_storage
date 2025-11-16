import pytest

from dto import auth_dto
from facades import ApplicationFacade

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
async def test_register(application_facade: ApplicationFacade):
    dto = auth_dto.RegistrationDTO(USERNAME, EMAIL, PASSWORD)

    await application_facade.register_user(dto)


@pytest.mark.asyncio
async def test_verify_email(application_facade: ApplicationFacade):
    await application_facade.verify_email(VERIFICATION_TOKEN)


@pytest.mark.asyncio
async def test_request_reset_code(application_facade: ApplicationFacade):
    response = await application_facade.request_password_reset(EMAIL)

    assert response.user_id == USER_ID
    assert response.username == USERNAME
    assert response.code == CODE


@pytest.mark.asyncio
async def test_validate_reset_code(application_facade: ApplicationFacade):
    dto = auth_dto.ResetCodeDTO(USER_ID, CODE)

    response = await application_facade.validate_reset_code(dto)

    assert response


@pytest.mark.asyncio
async def test_reset_password(application_facade: ApplicationFacade):
    dto = auth_dto.ResetPasswordDTO(USER_ID, PASSWORD)

    await application_facade.reset_password(dto)


@pytest.mark.asyncio
async def test_log_in(application_facade: ApplicationFacade):
    dto = auth_dto.LogInDTO(USERNAME, PASSWORD, USER_IP, USER_AGENT)

    response = await application_facade.log_in_user(dto)

    assert response.access_token == ACCESS_TOKEN
    assert response.refresh_token == REFRESH_TOKEN
    assert response.email == EMAIL
    assert response.browser == BROWSER
    assert response.verified


@pytest.mark.asyncio
async def test_log_out(application_facade: ApplicationFacade):
    await application_facade.log_out_user(ACCESS_TOKEN)


@pytest.mark.asyncio
async def test_resend_verification_mail(application_facade: ApplicationFacade):
    await application_facade.resend_verification_mail(ACCESS_TOKEN)


@pytest.mark.asyncio
async def test_auth(application_facade: ApplicationFacade):
    response = await application_facade.authenticate_user(ACCESS_TOKEN)

    assert response == USER_ID


@pytest.mark.asyncio
async def test_refresh(application_facade: ApplicationFacade):
    dto = auth_dto.RefreshDTO(REFRESH_TOKEN, USER_IP, USER_AGENT)

    response = await application_facade.refresh_tokens(dto)

    assert response.access_token == ACCESS_TOKEN
    assert response.refresh_token == REFRESH_TOKEN


@pytest.mark.asyncio
async def test_session_list(application_facade: ApplicationFacade):
    response = await application_facade.get_session_list(ACCESS_TOKEN)

    assert response[0].session_id == SESSION_ID
    assert response[0].user_ip == USER_IP
    assert response[0].browser == BROWSER
    assert response[0].created_at == TIMESTAMP


@pytest.mark.asyncio
async def test_revoke_session(application_facade: ApplicationFacade):
    dto = auth_dto.RevokeSessionDTO(ACCESS_TOKEN, SESSION_ID)

    await application_facade.revoke_session(dto)


@pytest.mark.asyncio
async def test_profile(application_facade: ApplicationFacade):
    response = await application_facade.get_user_profile(ACCESS_TOKEN)

    assert response.user_id == USER_ID
    assert response.username == USERNAME
    assert response.email == EMAIL
    assert response.verified
    assert response.registered_at == TIMESTAMP


@pytest.mark.asyncio
async def test_update_email(application_facade: ApplicationFacade):
    dto = auth_dto.UpdateEmailDTO(ACCESS_TOKEN, EMAIL)

    await application_facade.update_user_email(dto)


@pytest.mark.asyncio
async def test_update_password(application_facade: ApplicationFacade):
    dto = auth_dto.UpdatePasswordDTO(ACCESS_TOKEN, PASSWORD, PASSWORD)

    await application_facade.update_user_password(dto)


@pytest.mark.asyncio
async def test_delete_profile(application_facade: ApplicationFacade):
    response = await application_facade.delete_user_profile(ACCESS_TOKEN)

    assert response == USER_ID
