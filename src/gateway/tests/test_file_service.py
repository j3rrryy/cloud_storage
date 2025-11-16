import pytest

from dto import file_dto
from facades import ApplicationFacade

from .mocks import ETAG, FILE_ID, NAME, SIZE, TIMESTAMP, UPLOAD_ID, URL, USER_ID


@pytest.mark.asyncio
async def test_initiate_upload(application_facade: ApplicationFacade):
    dto = file_dto.InitiateUploadDTO(USER_ID, NAME, SIZE)

    response = await application_facade.initiate_file_upload(dto)

    assert response.upload_id == UPLOAD_ID
    assert response.part_size == SIZE
    assert len(response.parts) == 1
    assert response.parts[0].part_number == 1
    assert response.parts[0].url == URL


@pytest.mark.asyncio
async def test_complete_upload(application_facade: ApplicationFacade):
    dto = file_dto.CompleteUploadDTO(
        USER_ID, UPLOAD_ID, [file_dto.CompletePartDTO(1, ETAG)]
    )

    await application_facade.complete_file_upload(dto)


@pytest.mark.asyncio
async def test_abort_upload(application_facade: ApplicationFacade):
    dto = file_dto.AbortUploadDTO(USER_ID, UPLOAD_ID)

    await application_facade.abort_file_upload(dto)


@pytest.mark.asyncio
async def test_file_info(application_facade: ApplicationFacade):
    dto = file_dto.FileDTO(USER_ID, FILE_ID)

    response = await application_facade.get_file_info(dto)

    assert response.file_id == FILE_ID
    assert response.name == NAME
    assert response.size == SIZE
    assert response.uploaded_at == TIMESTAMP


@pytest.mark.asyncio
async def test_file_list(application_facade: ApplicationFacade):
    response = await application_facade.get_file_list(USER_ID)

    assert len(response) == 1
    assert response[0].file_id == FILE_ID
    assert response[0].name == NAME
    assert response[0].size == SIZE
    assert response[0].uploaded_at == TIMESTAMP


@pytest.mark.asyncio
async def test_download(application_facade: ApplicationFacade):
    dto = file_dto.FileDTO(USER_ID, FILE_ID)

    response = await application_facade.get_download_url(dto)

    assert response == URL


@pytest.mark.asyncio
async def test_delete(application_facade: ApplicationFacade):
    dto = file_dto.DeleteDTO(USER_ID, [FILE_ID])

    await application_facade.delete_files(dto)


@pytest.mark.asyncio
async def test_delete_with_no_files(application_facade: ApplicationFacade):
    dto = file_dto.DeleteDTO(USER_ID, [])

    await application_facade.delete_files(dto)


@pytest.mark.asyncio
async def test_delete_all(application_facade: ApplicationFacade):
    await application_facade.delete_all_files(USER_ID)
