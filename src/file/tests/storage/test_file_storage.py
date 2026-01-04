from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError
from grpc import StatusCode

from dto import request as request_dto
from dto import response as response_dto
from exceptions import BaseAppException

from ..mocks import (
    ETAG,
    FILE_ID,
    NAME,
    RELATIVE_URL,
    SIZE,
    TIMESTAMP,
    UPLOAD_ID,
    USER_ID,
)


@pytest.mark.asyncio
@patch("storage.file_storage.uuid4", MagicMock(return_value=FILE_ID))
async def test_initiate_upload(file_storage, client):
    dto = request_dto.InitiateUploadRequestDTO(USER_ID, NAME, SIZE)

    upload = await file_storage.initiate_upload(dto)

    assert upload == response_dto.InitiateUploadResponseDTO(
        FILE_ID, UPLOAD_ID, SIZE, [response_dto.UploadPartResponseDTO(1, RELATIVE_URL)]
    )
    client.create_multipart_upload.assert_awaited_once()
    client.generate_presigned_url.assert_awaited_once()


@pytest.mark.asyncio
async def test_initiate_upload_exception(client, file_storage):
    client.create_multipart_upload.side_effect = Exception("Details")
    dto = request_dto.InitiateUploadRequestDTO(USER_ID, NAME, SIZE)

    with pytest.raises(BaseAppException) as exc_info:
        await file_storage.initiate_upload(dto)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal storage error: Details"
    client.create_multipart_upload.assert_awaited_once()
    client.generate_presigned_url.assert_not_awaited()


@pytest.mark.asyncio
async def test_complete_upload(file_storage, client):
    dto = request_dto.CompleteUploadRequestDTO(
        USER_ID, UPLOAD_ID, [request_dto.CompletePartRequestDTO(1, ETAG)]
    )

    await file_storage.complete_upload(FILE_ID, dto)

    client.complete_multipart_upload.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_upload_no_upload(client, file_storage):
    client.complete_multipart_upload.side_effect = ClientError(
        error_response={"Error": {"Code": "NoSuchKey"}},
        operation_name="CompleteMultipartUpload",
    )
    dto = request_dto.CompleteUploadRequestDTO(
        USER_ID, UPLOAD_ID, [request_dto.CompletePartRequestDTO(1, ETAG)]
    )

    with pytest.raises(BaseAppException) as exc_info:
        await file_storage.complete_upload(FILE_ID, dto)

    assert exc_info.value.status_code == StatusCode.NOT_FOUND
    assert exc_info.value.details == "File not found"
    client.complete_multipart_upload.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_upload_client_error_exception(client, file_storage):
    client.complete_multipart_upload.side_effect = ClientError(
        error_response={"Error": {"Code": "Code"}},
        operation_name="CompleteMultipartUpload",
    )
    dto = request_dto.CompleteUploadRequestDTO(
        USER_ID, UPLOAD_ID, [request_dto.CompletePartRequestDTO(1, ETAG)]
    )

    with pytest.raises(BaseAppException) as exc_info:
        await file_storage.complete_upload(FILE_ID, dto)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert (
        exc_info.value.details
        == "Internal storage error: An error occurred (Code) when calling the CompleteMultipartUpload operation: Unknown"
    )
    client.complete_multipart_upload.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_upload_exception(client, file_storage):
    client.complete_multipart_upload.side_effect = Exception("Details")
    dto = request_dto.CompleteUploadRequestDTO(
        USER_ID, UPLOAD_ID, [request_dto.CompletePartRequestDTO(1, ETAG)]
    )

    with pytest.raises(BaseAppException) as exc_info:
        await file_storage.complete_upload(FILE_ID, dto)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal storage error: Details"
    client.complete_multipart_upload.assert_awaited_once()


@pytest.mark.asyncio
async def test_abort_upload(file_storage, client):
    await file_storage.abort_upload(FILE_ID, UPLOAD_ID)

    client.abort_multipart_upload.assert_awaited_once()


@pytest.mark.asyncio
async def test_abort_upload_no_upload(client, file_storage):
    client.abort_multipart_upload.side_effect = ClientError(
        error_response={"Error": {"Code": "NoSuchKey"}},
        operation_name="AbortMultipartUpload",
    )

    with pytest.raises(BaseAppException) as exc_info:
        await file_storage.abort_upload(FILE_ID, UPLOAD_ID)

    assert exc_info.value.status_code == StatusCode.NOT_FOUND
    assert exc_info.value.details == "File not found"
    client.abort_multipart_upload.assert_awaited_once()


@pytest.mark.asyncio
async def test_abort_upload_client_error_exception(client, file_storage):
    client.abort_multipart_upload.side_effect = ClientError(
        error_response={"Error": {"Code": "Code"}},
        operation_name="AbortMultipartUpload",
    )

    with pytest.raises(BaseAppException) as exc_info:
        await file_storage.abort_upload(FILE_ID, UPLOAD_ID)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert (
        exc_info.value.details
        == "Internal storage error: An error occurred (Code) when calling the AbortMultipartUpload operation: Unknown"
    )
    client.abort_multipart_upload.assert_awaited_once()


@pytest.mark.asyncio
async def test_abort_upload_exception(client, file_storage):
    client.abort_multipart_upload.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await file_storage.abort_upload(FILE_ID, UPLOAD_ID)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal storage error: Details"
    client.abort_multipart_upload.assert_awaited_once()


@pytest.mark.asyncio
async def test_download(client, file_storage):
    dto = response_dto.FileInfoResponseDTO(FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP)

    url = await file_storage.download(dto)

    assert url == RELATIVE_URL
    client.generate_presigned_url.assert_awaited_once()


@pytest.mark.asyncio
async def test_download_no_file(client, file_storage):
    client.generate_presigned_url.side_effect = ClientError(
        error_response={"Error": {"Code": "NoSuchKey"}},
        operation_name="GeneratePresignedURL",
    )
    dto = response_dto.FileInfoResponseDTO(FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP)

    with pytest.raises(BaseAppException) as exc_info:
        await file_storage.download(dto)

    assert exc_info.value.status_code == StatusCode.NOT_FOUND
    assert exc_info.value.details == "File not found"
    client.generate_presigned_url.assert_awaited_once()


@pytest.mark.asyncio
async def test_download_client_error_exception(client, file_storage):
    client.generate_presigned_url.side_effect = ClientError(
        error_response={"Error": {"Code": "Code"}},
        operation_name="GeneratePresignedURL",
    )
    dto = response_dto.FileInfoResponseDTO(FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP)

    with pytest.raises(BaseAppException) as exc_info:
        await file_storage.download(dto)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert (
        exc_info.value.details
        == "Internal storage error: An error occurred (Code) when calling the GeneratePresignedURL operation: Unknown"
    )
    client.generate_presigned_url.assert_awaited_once()


@pytest.mark.asyncio
async def test_download_exception(client, file_storage):
    client.generate_presigned_url.side_effect = Exception("Details")
    dto = response_dto.FileInfoResponseDTO(FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP)

    with pytest.raises(BaseAppException) as exc_info:
        await file_storage.download(dto)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal storage error: Details"
    client.generate_presigned_url.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete(file_storage, client):
    await file_storage.delete([FILE_ID])

    client.delete_objects.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_exception(client, file_storage):
    file_storage.logger = MagicMock()
    client.delete_objects.side_effect = Exception("Details")

    await file_storage.delete([FILE_ID])

    file_storage.logger.error.assert_called_once_with("Details")
