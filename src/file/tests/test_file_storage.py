from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from botocore.exceptions import ClientError
from grpc import StatusCode

from dto import request as request_dto
from dto import response as response_dto
from storage import FileStorage

from .mocks import (
    ETAG,
    FILE_ID,
    NAME,
    RELATIVE_URL,
    SIZE,
    TIMESTAMP,
    UPLOAD_ID,
    URL,
    USER_ID,
)


@pytest.mark.asyncio
@patch("storage.file_storage.uuid4", MagicMock(return_value=FILE_ID))
async def test_initiate_upload(mock_client):
    mock_client.create_multipart_upload = AsyncMock(
        return_value={"UploadId": UPLOAD_ID}
    )
    mock_client.generate_presigned_url.return_value = URL
    dto = request_dto.InitiateUploadRequestDTO(USER_ID, NAME, SIZE)

    upload = await FileStorage.initiate_upload(dto)  # type: ignore
    assert upload == response_dto.InitiateUploadResponseDTO(
        FILE_ID, UPLOAD_ID, SIZE, [response_dto.UploadPartResponseDTO(1, RELATIVE_URL)]
    )
    mock_client.create_multipart_upload.assert_awaited_once()
    mock_client.generate_presigned_url.assert_awaited_once()


@pytest.mark.asyncio
async def test_initiate_upload_exception(mock_client):
    mock_client.create_multipart_upload.side_effect = Exception("Details")
    dto = request_dto.InitiateUploadRequestDTO(USER_ID, NAME, SIZE)

    with pytest.raises(Exception) as exc_info:
        await FileStorage.initiate_upload(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal storage error, Details"
    mock_client.create_multipart_upload.assert_awaited_once()
    mock_client.generate_presigned_url.assert_not_awaited()


@pytest.mark.asyncio
async def test_complete_upload(mock_client):
    dto = request_dto.CompleteUploadRequestDTO(
        USER_ID, UPLOAD_ID, [request_dto.CompletePartRequestDTO(1, ETAG)]
    )
    await FileStorage.complete_upload(FILE_ID, dto)  # type: ignore
    mock_client.complete_multipart_upload.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_upload_no_upload(mock_client):
    mock_client.complete_multipart_upload.side_effect = ClientError(
        error_response={"Error": {"Code": "NoSuchKey"}},
        operation_name="CompleteMultipartUpload",
    )
    dto = request_dto.CompleteUploadRequestDTO(
        USER_ID, UPLOAD_ID, [request_dto.CompletePartRequestDTO(1, ETAG)]
    )

    with pytest.raises(Exception) as exc_info:
        await FileStorage.complete_upload(FILE_ID, dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.NOT_FOUND
    assert exc_info.value.args[1] == "Uploading file not found"
    mock_client.complete_multipart_upload.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_upload_client_error_exception(mock_client):
    mock_client.complete_multipart_upload.side_effect = ClientError(
        error_response={"Error": {"Code": "Code"}},
        operation_name="CompleteMultipartUpload",
    )
    dto = request_dto.CompleteUploadRequestDTO(
        USER_ID, UPLOAD_ID, [request_dto.CompletePartRequestDTO(1, ETAG)]
    )

    with pytest.raises(Exception) as exc_info:
        await FileStorage.complete_upload(FILE_ID, dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert (
        exc_info.value.args[1]
        == "Internal storage error, An error occurred (Code) when calling the CompleteMultipartUpload operation: Unknown"
    )
    mock_client.complete_multipart_upload.assert_awaited_once()


@pytest.mark.asyncio
async def test_abort_upload(mock_client):
    await FileStorage.abort_upload(FILE_ID, UPLOAD_ID)  # type: ignore
    mock_client.abort_multipart_upload.assert_awaited_once()


@pytest.mark.asyncio
async def test_abort_upload_no_upload(mock_client):
    mock_client.abort_multipart_upload.side_effect = ClientError(
        error_response={"Error": {"Code": "NoSuchKey"}},
        operation_name="AbortMultipartUpload",
    )

    with pytest.raises(Exception) as exc_info:
        await FileStorage.abort_upload(FILE_ID, UPLOAD_ID)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.NOT_FOUND
    assert exc_info.value.args[1] == "Uploading file not found"
    mock_client.abort_multipart_upload.assert_awaited_once()


@pytest.mark.asyncio
async def test_abort_upload_client_error_exception(mock_client):
    mock_client.abort_multipart_upload.side_effect = ClientError(
        error_response={"Error": {"Code": "Code"}},
        operation_name="AbortMultipartUpload",
    )

    with pytest.raises(Exception) as exc_info:
        await FileStorage.abort_upload(FILE_ID, UPLOAD_ID)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert (
        exc_info.value.args[1]
        == "Internal storage error, An error occurred (Code) when calling the AbortMultipartUpload operation: Unknown"
    )
    mock_client.abort_multipart_upload.assert_awaited_once()


@pytest.mark.asyncio
async def test_download(mock_client):
    generate_presigned_url = mock_client.generate_presigned_url
    generate_presigned_url.return_value = RELATIVE_URL
    dto = response_dto.FileInfoResponseDTO(FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP)
    url = await FileStorage.download(dto)  # type: ignore

    assert url == RELATIVE_URL
    mock_client.head_object.assert_awaited_once()
    generate_presigned_url.assert_awaited_once()


@pytest.mark.asyncio
async def test_download_no_file(mock_client):
    head_object = mock_client.head_object
    head_object.side_effect = ClientError(
        error_response={"Error": {"Code": "NoSuchKey"}}, operation_name="HeadObject"
    )
    dto = response_dto.FileInfoResponseDTO(FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP)

    with pytest.raises(Exception) as exc_info:
        await FileStorage.download(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.NOT_FOUND
    assert exc_info.value.args[1] == "File not found"
    head_object.assert_awaited_once()


@pytest.mark.asyncio
async def test_download_client_error_exception(mock_client):
    head_object = mock_client.head_object
    head_object.side_effect = ClientError(
        error_response={"Error": {"Code": "Code"}}, operation_name="HeadObject"
    )
    dto = response_dto.FileInfoResponseDTO(FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP)

    with pytest.raises(Exception) as exc_info:
        await FileStorage.download(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert (
        exc_info.value.args[1]
        == "Internal storage error, An error occurred (Code) when calling the HeadObject operation: Unknown"
    )
    head_object.assert_awaited_once()


@pytest.mark.asyncio
async def test_download_exception(mock_client):
    mock_client.generate_presigned_url.side_effect = Exception("Details")
    dto = response_dto.FileInfoResponseDTO(FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP)

    with pytest.raises(Exception) as exc_info:
        await FileStorage.download(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal storage error, Details"
    mock_client.head_object.assert_awaited_once()
    mock_client.generate_presigned_url.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete(mock_client):
    await FileStorage.delete([FILE_ID])  # type: ignore
    mock_client.delete_objects.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_exception(mock_client):
    FileStorage.logger = MagicMock()
    delete_objects = mock_client.delete_objects
    delete_objects.side_effect = Exception("Details")

    await FileStorage.delete([FILE_ID])  # type: ignore
    FileStorage.logger.error.assert_called_once_with("Details")


@pytest.mark.asyncio
async def test_delete_all(mock_client):
    async def mock_paginate(*args, **kwargs):
        yield {"Contents": [{"Key": FILE_ID}]}

    mock_paginator = MagicMock()
    mock_paginator.paginate = mock_paginate
    mock_client.get_paginator = MagicMock(return_value=mock_paginator)
    mock_client.delete_objects = AsyncMock()

    await FileStorage.delete_all(USER_ID)  # type: ignore
    mock_client.get_paginator.assert_called_once()
    mock_client.delete_objects.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_all_empty(mock_client):
    async def mock_paginate(*args, **kwargs):
        yield {}

    mock_paginator = MagicMock()
    mock_paginator.paginate = mock_paginate
    mock_client.get_paginator = MagicMock(return_value=mock_paginator)

    await FileStorage.delete_all(USER_ID)  # type: ignore
    mock_client.get_paginator.assert_called_once()


@pytest.mark.asyncio
async def test_delete_all_exception(mock_client):
    async def mock_paginate(*args, **kwargs):
        yield {"Contents": [{"Key": FILE_ID}]}

    mock_paginator = MagicMock()
    FileStorage.logger = MagicMock()
    mock_paginator.paginate = mock_paginate
    mock_client.get_paginator = MagicMock(return_value=mock_paginator)
    mock_client.delete_objects.side_effect = Exception("Details")

    await FileStorage.delete_all(USER_ID)  # type: ignore
    FileStorage.logger.error.assert_called_once_with("Details")
