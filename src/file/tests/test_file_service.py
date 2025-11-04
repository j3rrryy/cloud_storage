from unittest.mock import patch

import pytest

from dto import request as request_dto
from dto import response as response_dto
from service import FileService

from .mocks import (
    FILE_ID,
    NAME,
    RELATIVE_URL,
    SIZE,
    USER_ID,
    create_cache,
    create_repository,
    create_storage,
)


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_upload_file(mock_cache, mock_repository, mock_storage):
    dto = request_dto.UploadFileRequestDTO(USER_ID, NAME, SIZE)
    response = await FileService.upload_file(dto)

    assert response == RELATIVE_URL
    mock_cache.delete.assert_awaited_once()
    mock_storage.upload_file.assert_awaited_once()
    mock_repository.upload_file.assert_awaited_once()


@pytest.mark.asyncio
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_file_info(mock_cache, mock_repository):
    dto = request_dto.FileOperationRequestDTO(USER_ID, FILE_ID)
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
    dto = request_dto.FileOperationRequestDTO(USER_ID, FILE_ID)
    response = await FileService.file_info(dto)

    assert isinstance(response, response_dto.FileInfoResponseDTO)
    mock_cache.get.assert_awaited_once()


@pytest.mark.asyncio
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_file_list(mock_cache, mock_repository):
    response = await FileService.file_list(USER_ID)

    assert isinstance(response, tuple)
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

    assert isinstance(response, tuple)
    assert len(response) == 1
    assert isinstance(response[0], response_dto.FileInfoResponseDTO)
    mock_cache.get.assert_awaited_once()


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_download_file(mock_cache, mock_repository, mock_storage):
    dto = request_dto.FileOperationRequestDTO(USER_ID, FILE_ID)
    response = await FileService.download_file(dto)

    assert response == RELATIVE_URL
    mock_cache.get.assert_awaited_once()
    mock_repository.file_info.assert_awaited_once()
    mock_cache.set.assert_awaited_once()
    mock_storage.download_file.assert_awaited_once()


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_download_file_cached(mock_cache, mock_repository, mock_storage):
    mock_cache.get.return_value = mock_repository.file_info.return_value
    dto = request_dto.FileOperationRequestDTO(USER_ID, FILE_ID)
    response = await FileService.download_file(dto)

    assert response == RELATIVE_URL
    mock_cache.get.assert_awaited_once()
    mock_storage.download_file.assert_awaited_once()


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_delete_files(mock_cache, mock_repository, mock_storage):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])
    await FileService.delete_files(dto)

    mock_cache.delete.assert_awaited_once()
    mock_repository.delete_files.assert_awaited_once()
    mock_storage.delete_files.assert_awaited_once()
    mock_repository.delete_files.assert_awaited_once()
    mock_cache.delete_many.assert_awaited_once()


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_delete_files_empty_list(mock_cache, mock_repository, mock_storage):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [])
    await FileService.delete_files(dto)

    mock_cache.delete.assert_not_awaited()
    mock_repository.delete_files.assert_not_awaited()
    mock_storage.delete_files.assert_not_awaited()
    mock_repository.delete_files.assert_not_awaited()
    mock_cache.delete_many.assert_not_awaited()


@pytest.mark.asyncio
@patch("service.file_service.FileStorage", new_callable=create_storage)
@patch("service.file_service.FileRepository", new_callable=create_repository)
@patch("service.file_service.cache", new_callable=create_cache)
async def test_delete_all_files(mock_cache, mock_repository, mock_storage):
    await FileService.delete_all_files(USER_ID)
    mock_cache.delete_match.assert_awaited_once()
    mock_storage.delete_all_files.assert_called_once()
    mock_repository.delete_all_files.assert_awaited_once()
