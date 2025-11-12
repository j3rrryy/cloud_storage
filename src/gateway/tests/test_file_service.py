import pytest

from dto import file_dto

from .mocks import ETAG, FILE_ID, NAME, SIZE, TIMESTAMP, UPLOAD_ID, URL, USER_ID


@pytest.mark.asyncio
async def test_initiate_upload(file_service_v1):
    dto = file_dto.InitiateUploadDTO(USER_ID, NAME, SIZE)
    response = await file_service_v1.initiate_upload(dto)
    assert response.upload_id == UPLOAD_ID
    assert response.part_size == SIZE
    assert len(response.parts) == 1
    assert response.parts[0].part_number == 1
    assert response.parts[0].url == URL


@pytest.mark.asyncio
async def test_complete_upload(file_service_v1):
    dto = file_dto.CompleteUploadDTO(
        USER_ID, UPLOAD_ID, [file_dto.CompletePartDTO(1, ETAG)]
    )
    response = await file_service_v1.complete_upload(dto)
    assert response is None


@pytest.mark.asyncio
async def test_abort_upload(file_service_v1):
    dto = file_dto.AbortUploadDTO(USER_ID, UPLOAD_ID)
    response = await file_service_v1.abort_upload(dto)
    assert response is None


@pytest.mark.asyncio
async def test_file_info(file_service_v1):
    dto = file_dto.FileDTO(USER_ID, FILE_ID)
    response = await file_service_v1.file_info(dto)
    assert response.file_id == FILE_ID
    assert response.name == NAME
    assert response.size == SIZE
    assert response.uploaded_at == TIMESTAMP


@pytest.mark.asyncio
async def test_file_list(file_service_v1):
    response = await file_service_v1.file_list(USER_ID)
    assert len(response) == 1
    assert response[0].file_id == FILE_ID
    assert response[0].name == NAME
    assert response[0].size == SIZE
    assert response[0].uploaded_at == TIMESTAMP


@pytest.mark.asyncio
async def test_download(file_service_v1):
    dto = file_dto.FileDTO(USER_ID, FILE_ID)
    response = await file_service_v1.download(dto)
    assert response == URL


@pytest.mark.asyncio
async def test_delete(file_service_v1):
    dto = file_dto.DeleteDTO(USER_ID, {FILE_ID})
    response = await file_service_v1.delete(dto)
    assert response is None


@pytest.mark.asyncio
async def test_delete_with_no_files(file_service_v1):
    dto = file_dto.DeleteDTO(USER_ID, set())
    response = await file_service_v1.delete(dto)
    assert response is None
    file_service_v1._stub.Delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_all(file_service_v1):
    response = await file_service_v1.delete_all(USER_ID)
    assert response is None
