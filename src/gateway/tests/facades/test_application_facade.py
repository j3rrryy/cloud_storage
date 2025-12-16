import pytest

from dto import auth_dto, file_dto

from ..mocks import (
    ACCESS_TOKEN,
    BROWSER,
    CODE,
    EMAIL,
    ETAG,
    FILE_ID,
    NAME,
    PASSWORD,
    REFRESH_TOKEN,
    SESSION_ID,
    SIZE,
    TIMESTAMP,
    UPLOAD_ID,
    URL,
    USER_AGENT,
    USER_ID,
    USER_IP,
    USERNAME,
    VERIFICATION_TOKEN,
)


@pytest.mark.asyncio
async def test_register(application_facade):
    dto = auth_dto.RegistrationDTO(USERNAME, EMAIL, PASSWORD)

    await application_facade.register(dto)


@pytest.mark.asyncio
async def test_verify_email(application_facade):
    await application_facade.verify_email(VERIFICATION_TOKEN)


@pytest.mark.asyncio
async def test_request_reset_code(application_facade):
    response = await application_facade.request_reset_code(EMAIL)

    assert response == USER_ID


@pytest.mark.asyncio
async def test_validate_reset_code(application_facade):
    dto = auth_dto.ResetCodeDTO(USER_ID, CODE)

    response = await application_facade.validate_reset_code(dto)

    assert response


@pytest.mark.asyncio
async def test_reset_password(application_facade):
    dto = auth_dto.ResetPasswordDTO(USER_ID, PASSWORD)

    await application_facade.reset_password(dto)


@pytest.mark.asyncio
async def test_log_in(application_facade):
    dto = auth_dto.LogInDTO(USERNAME, PASSWORD, USER_IP, USER_AGENT)

    response = await application_facade.log_in(dto)

    assert response.access_token == ACCESS_TOKEN
    assert response.refresh_token == REFRESH_TOKEN
    assert response.email == EMAIL
    assert response.browser == BROWSER
    assert response.verified


@pytest.mark.asyncio
async def test_log_out(application_facade):
    await application_facade.log_out(ACCESS_TOKEN)


@pytest.mark.asyncio
async def test_resend_verification_mail(application_facade):
    await application_facade.resend_verification_mail(ACCESS_TOKEN)


@pytest.mark.asyncio
async def test_auth(application_facade):
    response = await application_facade.auth(ACCESS_TOKEN)

    assert response == USER_ID


@pytest.mark.asyncio
async def test_refresh(application_facade):
    dto = auth_dto.RefreshDTO(REFRESH_TOKEN, USER_IP, USER_AGENT)

    response = await application_facade.refresh(dto)

    assert response.access_token == ACCESS_TOKEN
    assert response.refresh_token == REFRESH_TOKEN


@pytest.mark.asyncio
async def test_session_list(application_facade):
    response = await application_facade.session_list(ACCESS_TOKEN)

    assert response[0].session_id == SESSION_ID
    assert response[0].user_ip == USER_IP
    assert response[0].browser == BROWSER
    assert response[0].created_at == TIMESTAMP


@pytest.mark.asyncio
async def test_revoke_session(application_facade):
    dto = auth_dto.RevokeSessionDTO(ACCESS_TOKEN, SESSION_ID)

    await application_facade.revoke_session(dto)


@pytest.mark.asyncio
async def test_profile(application_facade):
    response = await application_facade.profile(ACCESS_TOKEN)

    assert response.user_id == USER_ID
    assert response.username == USERNAME
    assert response.email == EMAIL
    assert response.verified
    assert response.registered_at == TIMESTAMP


@pytest.mark.asyncio
async def test_update_email(application_facade):
    dto = auth_dto.UpdateEmailDTO(ACCESS_TOKEN, EMAIL)

    await application_facade.update_email(dto)


@pytest.mark.asyncio
async def test_update_password(application_facade):
    dto = auth_dto.UpdatePasswordDTO(ACCESS_TOKEN, PASSWORD, PASSWORD)

    await application_facade.update_password(dto)


@pytest.mark.asyncio
async def test_delete_profile(application_facade):
    response = await application_facade.delete_profile(ACCESS_TOKEN)

    assert response is None


@pytest.mark.asyncio
async def test_initiate_upload(application_facade):
    dto = file_dto.InitiateUploadDTO(USER_ID, NAME, SIZE)

    response = await application_facade.initiate_upload(ACCESS_TOKEN, dto)

    assert response.upload_id == UPLOAD_ID
    assert response.part_size == SIZE
    assert len(response.parts) == 1
    assert response.parts[0].part_number == 1
    assert response.parts[0].url == URL


@pytest.mark.asyncio
async def test_complete_upload(application_facade):
    dto = file_dto.CompleteUploadDTO(
        USER_ID, UPLOAD_ID, [file_dto.CompletePartDTO(1, ETAG)]
    )

    await application_facade.complete_upload(ACCESS_TOKEN, dto)


@pytest.mark.asyncio
async def test_abort_upload(application_facade):
    dto = file_dto.AbortUploadDTO(USER_ID, UPLOAD_ID)

    await application_facade.abort_upload(ACCESS_TOKEN, dto)


@pytest.mark.asyncio
async def test_file_info(application_facade):
    dto = file_dto.FileDTO(USER_ID, FILE_ID)

    response = await application_facade.file_info(ACCESS_TOKEN, dto)

    assert response.file_id == FILE_ID
    assert response.name == NAME
    assert response.size == SIZE
    assert response.uploaded_at == TIMESTAMP


@pytest.mark.asyncio
async def test_file_list(application_facade):
    response = await application_facade.file_list(ACCESS_TOKEN)

    assert len(response) == 1
    assert response[0].file_id == FILE_ID
    assert response[0].name == NAME
    assert response[0].size == SIZE
    assert response[0].uploaded_at == TIMESTAMP


@pytest.mark.asyncio
async def test_download(application_facade):
    dto = file_dto.FileDTO(USER_ID, FILE_ID)

    response = await application_facade.download(ACCESS_TOKEN, dto)

    assert response == URL


@pytest.mark.asyncio
async def test_delete(application_facade):
    dto = file_dto.DeleteDTO(USER_ID, [FILE_ID])

    await application_facade.delete(ACCESS_TOKEN, dto)


@pytest.mark.asyncio
async def test_delete_all(application_facade):
    await application_facade.delete_all(ACCESS_TOKEN)
