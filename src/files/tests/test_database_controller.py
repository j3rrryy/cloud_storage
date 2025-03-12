from unittest.mock import patch

import pytest

from controllers import DatabaseController
from dto import request as request_dto
from dto import response as response_dto

from .mocks import (
    FILE_ID,
    NAME,
    PATH,
    SIZE,
    USER_ID,
    create_cache,
    create_database_crud,
)


@pytest.mark.asyncio
@patch("controllers.database.CRUD", new_callable=create_database_crud)
@patch("controllers.database.cache", new_callable=create_cache)
async def test_upload_file(mock_cache, mock_crud):
    dto = request_dto.UploadFileRequestDTO(USER_ID, NAME, PATH, SIZE)
    await DatabaseController.upload_file(dto)  # type: ignore
    mock_crud.upload_file.assert_called_once()
    mock_cache.delete.assert_called_once()


@pytest.mark.asyncio
@patch("controllers.database.CRUD", new_callable=create_database_crud)
@patch("controllers.database.cache", new_callable=create_cache)
async def test_file_info(mock_cache, mock_crud):
    dto = request_dto.FileOperationRequestDTO(USER_ID, FILE_ID)
    response = await DatabaseController.file_info(dto)  # type: ignore

    assert isinstance(response, response_dto.FileInfoResponseDTO)
    mock_cache.get.assert_called_once()
    mock_crud.file_info.assert_called_once()
    mock_cache.set.assert_called_once()


@pytest.mark.asyncio
@patch("controllers.database.CRUD", new_callable=create_database_crud)
@patch("controllers.database.cache", new_callable=create_cache)
async def test_file_info_cached(mock_cache, mock_crud):
    mock_cache.get.return_value = mock_crud.file_info.return_value
    dto = request_dto.FileOperationRequestDTO(USER_ID, FILE_ID)
    response = await DatabaseController.file_info(dto)  # type: ignore

    assert isinstance(response, response_dto.FileInfoResponseDTO)
    mock_cache.get.assert_called_once()


@pytest.mark.asyncio
@patch("controllers.database.CRUD", new_callable=create_database_crud)
@patch("controllers.database.cache", new_callable=create_cache)
async def test_file_list(mock_cache, mock_crud):
    response = await DatabaseController.file_list(USER_ID)  # type: ignore

    assert isinstance(response, tuple)
    assert len(response) == 1
    assert isinstance(response[0], response_dto.FileInfoResponseDTO)
    mock_cache.get.assert_called_once()
    mock_crud.file_list.assert_called_once()
    mock_cache.set.assert_called_once()


@pytest.mark.asyncio
@patch("controllers.database.CRUD", new_callable=create_database_crud)
@patch("controllers.database.cache", new_callable=create_cache)
async def test_file_list_cached(mock_cache, mock_crud):
    mock_cache.get.return_value = mock_crud.file_list.return_value
    response = await DatabaseController.file_list(USER_ID)  # type: ignore

    assert isinstance(response, tuple)
    assert len(response) == 1
    assert isinstance(response[0], response_dto.FileInfoResponseDTO)
    mock_cache.get.assert_called_once()


@pytest.mark.asyncio
@patch("controllers.database.CRUD", new_callable=create_database_crud)
@patch("controllers.database.cache", new_callable=create_cache)
async def test_download_file(mock_cache, mock_crud):
    dto = request_dto.FileOperationRequestDTO(USER_ID, FILE_ID)
    response = await DatabaseController.download_file(dto)  # type: ignore

    assert isinstance(response, response_dto.FileInfoResponseDTO)
    mock_cache.get.assert_called_once()
    mock_crud.file_info.assert_called_once()
    mock_cache.set.assert_called_once()


@pytest.mark.asyncio
@patch("controllers.database.CRUD", new_callable=create_database_crud)
@patch("controllers.database.cache", new_callable=create_cache)
async def test_download_file_cached(mock_cache, mock_crud):
    mock_cache.get.return_value = mock_crud.file_info.return_value
    dto = request_dto.FileOperationRequestDTO(USER_ID, FILE_ID)
    response = await DatabaseController.download_file(dto)  # type: ignore

    assert isinstance(response, response_dto.FileInfoResponseDTO)
    mock_cache.get.assert_called_once()


@pytest.mark.asyncio
@patch("controllers.database.CRUD", new_callable=create_database_crud)
@patch("controllers.database.cache", new_callable=create_cache)
async def test_delete_files(mock_cache, mock_crud):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])
    response = await DatabaseController.delete_files(dto)  # type: ignore

    assert isinstance(response, response_dto.DeleteFilesResponseDTO)
    mock_crud.delete_files.assert_called_once()
    mock_cache.delete.assert_called_once()
    mock_cache.delete_many.assert_called_once()


@pytest.mark.asyncio
@patch("controllers.database.CRUD", new_callable=create_database_crud)
@patch("controllers.database.cache", new_callable=create_cache)
async def test_delete_all_files(mock_cache, mock_crud):
    await DatabaseController.delete_all_files(USER_ID)  # type: ignore
    mock_crud.delete_all_files.assert_called_once()
    mock_cache.delete.assert_called_once()
    assert mock_cache.delete_match.call_count == 2
