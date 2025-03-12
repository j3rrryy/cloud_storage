from unittest.mock import patch

import pytest

from controllers import StorageController
from dto import request as request_dto
from dto import response as response_dto

from .mocks import (
    FILE_ID,
    NAME,
    PATH,
    RELATIVE_URL,
    SIZE,
    TIMESTAMP,
    USER_ID,
    create_storage_crud,
)


@pytest.mark.asyncio
@patch("controllers.storage.CRUD", new_callable=create_storage_crud)
async def test_upload_file(mock_crud):
    dto = request_dto.UploadFileRequestDTO(USER_ID, NAME, PATH, SIZE)
    response = await StorageController.upload_file(dto)  # type: ignore
    assert response == RELATIVE_URL
    mock_crud.upload_file.assert_called_once()


@pytest.mark.asyncio
@patch("controllers.storage.CRUD", new_callable=create_storage_crud)
async def test_download_file(mock_crud):
    dto = response_dto.FileInfoResponseDTO(
        FILE_ID, USER_ID, NAME, PATH + NAME, SIZE, TIMESTAMP
    )
    response = await StorageController.download_file(dto)  # type: ignore
    assert response == RELATIVE_URL
    mock_crud.download_file.assert_called_once()


@pytest.mark.asyncio
@patch("controllers.storage.CRUD", new_callable=create_storage_crud)
async def test_delete_files(mock_crud):
    dto = response_dto.DeleteFilesResponseDTO(USER_ID, [PATH + NAME])
    await StorageController.delete_files(dto)  # type: ignore
    mock_crud.delete_files.assert_called_once()


@pytest.mark.asyncio
@patch("controllers.storage.CRUD", new_callable=create_storage_crud)
async def test_delete_all_files(mock_crud):
    await StorageController.delete_all_files(USER_ID)  # type: ignore
    mock_crud.delete_all_files.assert_called_once()
