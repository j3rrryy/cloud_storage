from unittest.mock import patch

import pytest
from grpc import StatusCode

from dto import request as request_dto
from dto import response as response_dto
from service import FileService

from .mocks import (
    ETAG,
    FILE_ID,
    NAME,
    RELATIVE_URL,
    SIZE,
    UPLOAD_ID,
    USER_ID,
    create_cache,
    create_repository,
    create_storage,
)


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_initiate_upload(mock_cache, mock_repository, mock_storage):
    dto = request_dto.InitiateUploadRequestDTO(USER_ID, NAME, SIZE)

    response = await FileService.initiate_upload(dto)

    assert isinstance(response, response_dto.InitiateUploadResponseDTO)
    mock_repository.check_if_name_is_taken.assert_awaited_once()
    mock_storage.initiate_upload.assert_awaited_once()
    mock_cache.set.assert_awaited_once()


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_initiate_upload_file_too_large(
    mock_cache, mock_repository, mock_storage
):
    dto = request_dto.InitiateUploadRequestDTO(
        USER_ID, NAME, FileService.MAX_FILE_SIZE + 1
    )

    with pytest.raises(Exception) as exc_info:
        await FileService.initiate_upload(dto)

    assert exc_info.value.args[0] == StatusCode.INVALID_ARGUMENT
    assert exc_info.value.args[1] == "File too large"
    mock_repository.check_if_name_is_taken.assert_not_awaited()
    mock_storage.initiate_upload.assert_not_awaited()
    mock_cache.set.assert_not_awaited()


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_complete_upload(mock_cache, mock_repository, mock_storage):
    mock_cache.get.return_value = mock_cache.get.return_value = (
        request_dto.InitiatedUploadRequestDTO(FILE_ID, USER_ID, NAME, SIZE)
    )
    dto = request_dto.CompleteUploadRequestDTO(
        USER_ID, UPLOAD_ID, [request_dto.CompletePartRequestDTO(1, ETAG)]
    )

    await FileService.complete_upload(dto)

    mock_cache.get.assert_awaited_once()
    mock_storage.complete_upload.assert_awaited_once()
    mock_repository.complete_upload.assert_awaited_once()
    mock_cache.delete_many.assert_awaited_once()


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_complete_upload_no_parts(mock_cache, mock_repository, mock_storage):
    dto = request_dto.CompleteUploadRequestDTO(USER_ID, UPLOAD_ID, [])

    with pytest.raises(Exception) as exc_info:
        await FileService.complete_upload(dto)

    assert exc_info.value.args[0] == StatusCode.INVALID_ARGUMENT
    assert exc_info.value.args[1] == "Uploaded parts list cannot be empty"
    mock_cache.get.assert_not_awaited()
    mock_storage.complete_upload.assert_not_awaited()
    mock_repository.complete_upload.assert_not_awaited()
    mock_cache.delete_many.assert_not_awaited()


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_complete_upload_not_cached(mock_cache, mock_repository, mock_storage):
    dto = request_dto.CompleteUploadRequestDTO(
        USER_ID, UPLOAD_ID, [request_dto.CompletePartRequestDTO(1, ETAG)]
    )

    with pytest.raises(Exception) as exc_info:
        await FileService.complete_upload(dto)

    assert exc_info.value.args[0] == StatusCode.NOT_FOUND
    assert exc_info.value.args[1] == "Uploading file not found"
    mock_cache.get.assert_awaited_once()
    mock_storage.complete_upload.assert_not_awaited()
    mock_repository.complete_upload.assert_not_awaited()
    mock_cache.delete_many.assert_not_awaited()


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_abort_upload(mock_cache, mock_storage):
    mock_cache.get.return_value = mock_cache.get.return_value = (
        request_dto.InitiatedUploadRequestDTO(FILE_ID, USER_ID, NAME, SIZE)
    )
    dto = request_dto.AbortUploadRequestDTO(USER_ID, UPLOAD_ID)

    await FileService.abort_upload(dto)

    mock_cache.get.assert_awaited_once()
    mock_storage.abort_upload.assert_awaited_once()
    mock_cache.delete.assert_awaited_once()


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_abort_upload_not_cached(mock_cache, mock_storage):
    dto = request_dto.AbortUploadRequestDTO(USER_ID, UPLOAD_ID)

    with pytest.raises(Exception) as exc_info:
        await FileService.abort_upload(dto)

    assert exc_info.value.args[0] == StatusCode.NOT_FOUND
    assert exc_info.value.args[1] == "Uploading file not found"
    mock_cache.get.assert_awaited_once()
    mock_storage.abort_upload.assert_not_awaited()
    mock_cache.delete.assert_not_awaited()


@pytest.mark.asyncio
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_file_info(mock_cache, mock_repository):
    dto = request_dto.FileRequestDTO(USER_ID, FILE_ID)

    response = await FileService.file_info(dto)

    assert isinstance(response, response_dto.FileInfoResponseDTO)
    mock_cache.get.assert_awaited_once()
    mock_repository.file_info.assert_awaited_once()
    mock_cache.set.assert_awaited_once()


@pytest.mark.asyncio
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_file_info_cached(mock_cache, mock_repository):
    mock_cache.get.return_value = mock_repository.file_info.return_value
    dto = request_dto.FileRequestDTO(USER_ID, FILE_ID)

    response = await FileService.file_info(dto)

    assert isinstance(response, response_dto.FileInfoResponseDTO)
    mock_cache.get.assert_awaited_once()


@pytest.mark.asyncio
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_file_list(mock_cache, mock_repository):
    response = await FileService.file_list(USER_ID)

    assert len(response) == 1
    assert isinstance(response[0], response_dto.FileInfoResponseDTO)
    mock_cache.get.assert_awaited_once()
    mock_repository.file_list.assert_awaited_once()
    mock_cache.set.assert_awaited_once()


@pytest.mark.asyncio
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_file_list_cached(mock_cache, mock_repository):
    mock_cache.get.return_value = mock_repository.file_list.return_value

    response = await FileService.file_list(USER_ID)

    assert len(response) == 1
    assert isinstance(response[0], response_dto.FileInfoResponseDTO)
    mock_cache.get.assert_awaited_once()


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_download(mock_cache, mock_repository, mock_storage):
    dto = request_dto.FileRequestDTO(USER_ID, FILE_ID)

    response = await FileService.download(dto)

    assert response == RELATIVE_URL
    mock_cache.get.assert_awaited_once()
    mock_repository.file_info.assert_awaited_once()
    mock_cache.set.assert_awaited_once()
    mock_storage.download.assert_awaited_once()


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_download_cached(mock_cache, mock_repository, mock_storage):
    mock_cache.get.return_value = mock_repository.file_info.return_value
    dto = request_dto.FileRequestDTO(USER_ID, FILE_ID)

    response = await FileService.download(dto)

    assert response == RELATIVE_URL
    mock_cache.get.assert_awaited_once()
    mock_storage.download.assert_awaited_once()


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_delete(mock_cache, mock_repository, mock_storage):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])

    await FileService.delete(dto)

    mock_repository.validate_user_files.assert_awaited_once()
    mock_storage.delete.assert_called_once()
    mock_repository.delete.assert_awaited_once()
    mock_cache.delete.assert_awaited_once()
    mock_cache.delete_many.assert_awaited_once()


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_delete_with_no_files(mock_cache, mock_repository, mock_storage):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [])

    await FileService.delete(dto)

    mock_repository.validate_user_files.assert_not_awaited()
    mock_storage.delete.assert_not_awaited()
    mock_repository.delete.assert_not_awaited()
    mock_cache.delete.assert_not_awaited()
    mock_cache.delete_many.assert_not_awaited()


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_delete_all(mock_cache, mock_repository, mock_storage):
    await FileService.delete_all(USER_ID)

    mock_repository.delete_all.assert_awaited_once()
    mock_storage.delete.assert_called_once()
    mock_cache.delete_match.assert_awaited_once()
