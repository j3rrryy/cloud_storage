import pytest

from dto import file_dto

from .mocks import FILE_ID, NAME, PATH, SIZE, TIMESTAMP, URL, USER_ID


@pytest.mark.asyncio
async def test_upload_file(file_service_v1):
    dto = file_dto.UploadFileDTO(USER_ID, NAME, PATH, SIZE)
    response = await file_service_v1.upload_file(dto)
    assert response == URL


@pytest.mark.asyncio
async def test_file_info(file_service_v1):
    dto = file_dto.FileDTO(USER_ID, FILE_ID)
    response = await file_service_v1.file_info(dto)
    assert response.file_id == FILE_ID
    assert response.name == NAME
    assert response.path == PATH
    assert response.size == SIZE
    assert response.uploaded_at == TIMESTAMP


@pytest.mark.asyncio
async def test_file_list(file_service_v1):
    response = await file_service_v1.file_list(USER_ID)
    first_file = next(response)
    assert first_file.file_id == FILE_ID
    assert first_file.name == NAME
    assert first_file.path == PATH
    assert first_file.size == SIZE
    assert first_file.uploaded_at == TIMESTAMP


@pytest.mark.asyncio
async def test_download_file(file_service_v1):
    dto = file_dto.FileDTO(USER_ID, FILE_ID)
    response = await file_service_v1.download_file(dto)
    assert response == URL


@pytest.mark.asyncio
async def test_delete_files(file_service_v1):
    dto = file_dto.DeleteFilesDTO(USER_ID, {FILE_ID})
    response = await file_service_v1.delete_files(dto)
    assert response is None


@pytest.mark.asyncio
async def test_delete_all_files(file_service_v1):
    response = await file_service_v1.delete_all_files(USER_ID)
    assert response is None
