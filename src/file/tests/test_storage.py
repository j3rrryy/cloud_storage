import pytest
from grpc import StatusCode

from dto import request as request_dto
from dto import response as response_dto
from storage import FileStorage

from .mocks import FILE_ID, NAME, PATH, SIZE, TIMESTAMP, URL, USER_ID


@pytest.mark.asyncio
async def test_upload_file(mock_client):
    dto = request_dto.UploadFileRequestDTO(USER_ID, NAME, PATH, SIZE)
    mock_client.generate_presigned_url.return_value = URL
    url = await FileStorage.upload_file(dto, mock_client)

    assert url == URL
    mock_client.generate_presigned_url.assert_called_once()


@pytest.mark.asyncio
async def test_upload_file_exception(mock_client):
    dto = request_dto.UploadFileRequestDTO(USER_ID, NAME, PATH, SIZE)
    mock_client.generate_presigned_url.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileStorage.upload_file(dto, mock_client)

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal storage error, Details"
    mock_client.generate_presigned_url.assert_called_once()


@pytest.mark.asyncio
async def test_download_file(mock_client):
    dto = response_dto.FileInfoResponseDTO(
        FILE_ID, USER_ID, NAME, PATH, SIZE, TIMESTAMP
    )
    mock_client.generate_presigned_url.return_value = URL
    url = await FileStorage.download_file(dto, mock_client)

    assert url == URL
    mock_client.head_object.assert_called_once()
    mock_client.generate_presigned_url.assert_called_once()


@pytest.mark.asyncio
async def test_download_file_not_file(mock_client):
    dto = response_dto.FileInfoResponseDTO(
        FILE_ID, USER_ID, NAME, PATH, SIZE, TIMESTAMP
    )
    mock_client.head_object.side_effect = Exception

    with pytest.raises(Exception) as exc_info:
        await FileStorage.download_file(dto, mock_client)

    assert exc_info.value.args[0] == StatusCode.NOT_FOUND
    assert exc_info.value.args[1] == "File not found"
    mock_client.head_object.assert_called_once()


@pytest.mark.asyncio
async def test_download_file_exception(mock_client):
    dto = response_dto.FileInfoResponseDTO(
        FILE_ID, USER_ID, NAME, PATH, SIZE, TIMESTAMP
    )
    mock_client.generate_presigned_url.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileStorage.download_file(dto, mock_client)

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal storage error, Details"
    mock_client.head_object.assert_called_once()
    mock_client.generate_presigned_url.assert_called_once()


@pytest.mark.asyncio
async def test_delete_files(mock_client):
    dto = response_dto.DeleteFilesResponseDTO(USER_ID, [PATH])
    await FileStorage.delete_files(dto, mock_client)
    mock_client.delete_object.assert_called_once()


@pytest.mark.asyncio
async def test_delete_files_exception(mock_client):
    dto = response_dto.DeleteFilesResponseDTO(USER_ID, [PATH])
    mock_client.delete_object.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileStorage.delete_files(dto, mock_client)

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal storage error, Details"
    mock_client.delete_object.assert_called_once()


@pytest.mark.asyncio
async def test_delete_all_files(mock_client):
    async def mock_paginate(*args, **kwargs):
        yield {"Contents": [{"Key": f"{USER_ID}{PATH}{NAME}"}]}

    mock_client.get_paginator.return_value.paginate = mock_paginate
    await FileStorage.delete_all_files(USER_ID, mock_client)
    mock_client.get_paginator.assert_called_once()
    mock_client.delete_objects.assert_called_once()


@pytest.mark.asyncio
async def test_delete_all_files_empty(mock_client):
    async def mock_paginate(*args, **kwargs):
        yield {}

    mock_client.get_paginator.return_value.paginate = mock_paginate
    await FileStorage.delete_all_files(USER_ID, mock_client)
    mock_client.get_paginator.assert_called_once()


@pytest.mark.asyncio
async def test_delete_all_files_exception(mock_client):
    async def mock_paginate(*args, **kwargs):
        yield {"Contents": [{"Key": f"{USER_ID}{PATH}{NAME}"}]}

    mock_client.get_paginator.return_value.paginate = mock_paginate
    mock_client.delete_objects.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileStorage.delete_all_files(USER_ID, mock_client)

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal storage error, Details"
    mock_client.get_paginator.assert_called_once()
    mock_client.delete_objects.assert_called_once()
