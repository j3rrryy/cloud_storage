from unittest.mock import MagicMock

import pytest
from google.protobuf.empty_pb2 import Empty
from google.protobuf.timestamp_pb2 import Timestamp

from proto import file_pb2 as pb2

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
async def test_initiate_upload(file_controller):
    request = pb2.InitiateUploadRequest(user_id=USER_ID, name=NAME, size=SIZE)

    response = await file_controller.InitiateUpload(request, MagicMock())

    assert response == pb2.InitiateUploadResponse(
        upload_id=UPLOAD_ID,
        part_size=SIZE,
        parts=[pb2.UploadPart(part_number=1, url=RELATIVE_URL)],
    )


@pytest.mark.asyncio
async def test_complete_upload(file_controller):
    request = pb2.CompleteUploadRequest(
        user_id=USER_ID,
        upload_id=NAME,
        parts=[pb2.CompletePart(part_number=1, etag=ETAG)],
    )

    response = await file_controller.CompleteUpload(request, MagicMock())

    assert response == Empty()


@pytest.mark.asyncio
async def test_abort_upload(file_controller):
    request = pb2.AbortUploadRequest(user_id=USER_ID, upload_id=UPLOAD_ID)

    response = await file_controller.AbortUpload(request, MagicMock())

    assert response == Empty()


@pytest.mark.asyncio
async def test_file_list(cache, file_controller):
    cache.get.return_value = None
    request = pb2.UserId(user_id=USER_ID)

    response = await file_controller.FileList(request, MagicMock())

    assert response == pb2.FileListResponse(
        files=(
            pb2.FileInfo(
                file_id=FILE_ID,
                name=NAME,
                size=SIZE,
                uploaded_at=Timestamp(seconds=int(TIMESTAMP.timestamp())),
            ),
        )
    )


@pytest.mark.asyncio
async def test_download(file_controller):
    request = pb2.FileRequest(user_id=USER_ID, file_id=FILE_ID)

    response = await file_controller.Download(request, MagicMock())

    assert response == pb2.URL(url=RELATIVE_URL)


@pytest.mark.asyncio
async def test_delete(file_controller):
    request = pb2.DeleteRequest(user_id=USER_ID, file_ids=[FILE_ID])

    response = await file_controller.Delete(request, MagicMock())

    assert response == Empty()


@pytest.mark.asyncio
async def test_delete_all(file_controller):
    request = pb2.UserId(user_id=USER_ID)

    response = await file_controller.DeleteAll(request, MagicMock())

    assert response == Empty()
