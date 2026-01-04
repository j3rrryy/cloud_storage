import pytest
from grpc import StatusCode

from dto import request as request_dto
from exceptions import BaseAppException
from settings import Settings

from ..mocks import ETAG, NAME, UPLOAD_ID, USER_ID


@pytest.mark.asyncio
async def test_initiate_upload_file_too_large(file_service):
    dto = request_dto.InitiateUploadRequestDTO(
        USER_ID, NAME, Settings.MAX_FILE_SIZE + 1
    )

    with pytest.raises(BaseAppException) as exc_info:
        await file_service.initiate_upload(dto)

    assert exc_info.value.status_code == StatusCode.INVALID_ARGUMENT
    assert exc_info.value.details == "File too large"


@pytest.mark.asyncio
async def test_complete_upload_file_not_found(cache, file_service):
    cache.get.return_value = None
    dto = request_dto.CompleteUploadRequestDTO(
        USER_ID, UPLOAD_ID, [request_dto.CompletePartRequestDTO(1, ETAG)]
    )

    with pytest.raises(BaseAppException) as exc_info:
        await file_service.complete_upload(dto)

    assert exc_info.value.status_code == StatusCode.NOT_FOUND
    assert exc_info.value.details == "File not found"


@pytest.mark.asyncio
async def test_abort_upload_file_not_found(cache, file_service):
    cache.get.return_value = None
    dto = request_dto.AbortUploadRequestDTO(USER_ID, UPLOAD_ID)

    with pytest.raises(BaseAppException) as exc_info:
        await file_service.abort_upload(dto)

    assert exc_info.value.status_code == StatusCode.NOT_FOUND
    assert exc_info.value.details == "File not found"


@pytest.mark.asyncio
async def test_delete_with_no_files(mocked_file_repository, file_service):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [])

    await file_service.delete(dto)

    mocked_file_repository.validate_user_files.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_all_with_no_files(mocked_file_repository, file_service, cache):
    mocked_file_repository.delete_all.return_value = []

    await file_service.delete_all(USER_ID)

    cache.delete_many.assert_not_awaited()
