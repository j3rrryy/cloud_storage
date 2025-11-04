from unittest.mock import AsyncMock, MagicMock

import pytest
from botocore.exceptions import ClientError
from grpc import StatusCode

from dto import response as response_dto
from storage import FileStorage

from .mocks import FILE_ID, NAME, SIZE, TIMESTAMP, URL, USER_ID


@pytest.mark.asyncio
async def test_upload_file(mock_client):
    generate_presigned_url = mock_client.generate_presigned_url
    generate_presigned_url.return_value = URL
    url = await FileStorage.upload_file(FILE_ID)  # type: ignore

    assert url == URL
    generate_presigned_url.assert_awaited_once()


@pytest.mark.asyncio
async def test_upload_file_exception(mock_client):
    generate_presigned_url = mock_client.generate_presigned_url
    generate_presigned_url.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileStorage.upload_file(FILE_ID)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal storage error, Details"
    generate_presigned_url.assert_awaited_once()


@pytest.mark.asyncio
async def test_download_file(mock_client):
    dto = response_dto.FileInfoResponseDTO(FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP)
    generate_presigned_url = mock_client.generate_presigned_url
    generate_presigned_url.return_value = URL
    url = await FileStorage.download_file(dto)  # type: ignore

    assert url == URL
    mock_client.head_object.assert_awaited_once()
    generate_presigned_url.assert_awaited_once()


@pytest.mark.asyncio
async def test_download_file_not_file(mock_client):
    dto = response_dto.FileInfoResponseDTO(FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP)
    head_object = mock_client.head_object
    head_object.side_effect = ClientError(
        error_response={"Error": {"Code": "NoSuchKey"}}, operation_name="HeadObject"
    )

    with pytest.raises(Exception) as exc_info:
        await FileStorage.download_file(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.NOT_FOUND
    assert exc_info.value.args[1] == "File not found"
    head_object.assert_awaited_once()


@pytest.mark.asyncio
async def test_download_file_client_error_exception(mock_client):
    dto = response_dto.FileInfoResponseDTO(FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP)
    head_object = mock_client.head_object
    head_object.side_effect = ClientError(
        error_response={"Error": {"Code": "Code"}}, operation_name="HeadObject"
    )

    with pytest.raises(Exception) as exc_info:
        await FileStorage.download_file(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert (
        exc_info.value.args[1]
        == "Internal storage error, An error occurred (Code) when calling the HeadObject operation: Unknown"
    )
    head_object.assert_awaited_once()


@pytest.mark.asyncio
async def test_download_file_exception(mock_client):
    dto = response_dto.FileInfoResponseDTO(FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP)
    generate_presigned_url = mock_client.generate_presigned_url
    generate_presigned_url.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileStorage.download_file(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal storage error, Details"
    mock_client.head_object.assert_awaited_once()
    generate_presigned_url.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_files(mock_client):
    await FileStorage.delete_files([FILE_ID])  # type: ignore
    mock_client.delete_objects.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_files_exception(mock_client):
    FileStorage.logger = MagicMock()
    delete_objects = mock_client.delete_objects
    delete_objects.side_effect = Exception("Details")

    await FileStorage.delete_files([FILE_ID])  # type: ignore
    FileStorage.logger.error.assert_called_once_with("Details")


@pytest.mark.asyncio
async def test_delete_all_files(mock_client):
    async def mock_paginate(*args, **kwargs):
        yield {"Contents": [{"Key": FILE_ID}]}

    mock_paginator = MagicMock()
    mock_paginator.paginate = mock_paginate
    mock_client.get_paginator = MagicMock(return_value=mock_paginator)
    mock_client.delete_objects = AsyncMock()

    await FileStorage.delete_all_files(USER_ID)  # type: ignore
    mock_client.get_paginator.assert_called_once()
    mock_client.delete_objects.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_all_files_empty(mock_client):
    async def mock_paginate(*args, **kwargs):
        yield {}

    mock_paginator = MagicMock()
    mock_paginator.paginate = mock_paginate
    mock_client.get_paginator = MagicMock(return_value=mock_paginator)

    await FileStorage.delete_all_files(USER_ID)  # type: ignore
    mock_client.get_paginator.assert_called_once()


@pytest.mark.asyncio
async def test_delete_all_files_exception(mock_client):
    async def mock_paginate(*args, **kwargs):
        yield {"Contents": [{"Key": FILE_ID}]}

    mock_paginator = MagicMock()
    FileStorage.logger = MagicMock()
    mock_paginator.paginate = mock_paginate
    mock_client.get_paginator = MagicMock(return_value=mock_paginator)
    mock_client.delete_objects.side_effect = Exception("Details")

    await FileStorage.delete_all_files(USER_ID)  # type: ignore
    FileStorage.logger.error.assert_called_once_with("Details")
