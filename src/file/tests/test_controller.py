from unittest.mock import MagicMock, patch

import pytest
from google.protobuf.empty_pb2 import Empty
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import ServicerContext

from proto import file_pb2 as pb2

from .mocks import (
    FILE_ID,
    NAME,
    PATH,
    RELATIVE_URL,
    SIZE,
    TIMESTAMP,
    USER_ID,
    create_cache,
    create_repository,
    create_storage,
)


@pytest.mark.asyncio
async def test_upload_file(file_controller):
    with (
        patch("service.file.FileRepository", new_callable=create_repository),
        patch("service.file.FileStorage", new_callable=create_storage),
        patch("service.file.cache", new_callable=create_cache),
    ):
        request = pb2.UploadFileRequest(
            user_id=USER_ID, name=NAME, path=PATH, size=SIZE
        )
        response = await file_controller.UploadFile(request, MagicMock(ServicerContext))
        assert response == pb2.FileURLResponse(url=RELATIVE_URL)


@pytest.mark.asyncio
async def test_file_info(file_controller):
    with (
        patch("service.file.FileRepository", new_callable=create_repository),
        patch("service.file.cache", new_callable=create_cache),
    ):
        request = pb2.FileOperationRequest(user_id=USER_ID, file_id=FILE_ID)
        response = await file_controller.FileInfo(request, MagicMock(ServicerContext))
        assert response == pb2.FileInfoResponse(
            file_id=FILE_ID,
            name=NAME,
            path=PATH,
            size=SIZE,
            uploaded=Timestamp(seconds=int(TIMESTAMP.timestamp())),
        )


@pytest.mark.asyncio
async def test_file_list(file_controller):
    with (
        patch("service.file.FileRepository", new_callable=create_repository),
        patch("service.file.cache", new_callable=create_cache),
    ):
        request = pb2.UserId(user_id=USER_ID)
        response = await file_controller.FileList(request, MagicMock(ServicerContext))
        assert response == pb2.FileListResponse(
            files=(
                pb2.FileInfoResponse(
                    file_id=FILE_ID,
                    name=NAME,
                    path=PATH,
                    size=SIZE,
                    uploaded=Timestamp(seconds=int(TIMESTAMP.timestamp())),
                ),
            )
        )


@pytest.mark.asyncio
async def test_download_file(file_controller):
    with (
        patch("service.file.FileRepository", new_callable=create_repository),
        patch("service.file.FileStorage", new_callable=create_storage),
        patch("service.file.cache", new_callable=create_cache),
    ):
        request = pb2.FileOperationRequest(user_id=USER_ID, file_id=FILE_ID)
        response = await file_controller.DownloadFile(
            request, MagicMock(ServicerContext)
        )
        assert response == pb2.FileURLResponse(url=RELATIVE_URL)


@pytest.mark.asyncio
async def test_delete_files(file_controller):
    with (
        patch("service.file.FileRepository", new_callable=create_repository),
        patch("service.file.FileStorage", new_callable=create_storage),
        patch("service.file.cache", new_callable=create_cache),
    ):
        request = pb2.DeleteFilesRequest(user_id=USER_ID, file_ids=(FILE_ID,))
        response = await file_controller.DeleteFiles(
            request, MagicMock(ServicerContext)
        )
        assert response == Empty()


@pytest.mark.asyncio
async def test_delete_all_files(file_controller):
    with (
        patch("service.file.FileRepository", new_callable=create_repository),
        patch("service.file.FileStorage", new_callable=create_storage),
        patch("service.file.cache", new_callable=create_cache),
    ):
        request = pb2.UserId(user_id=USER_ID)
        response = await file_controller.DeleteAllFiles(
            request, MagicMock(ServicerContext)
        )
        assert response == Empty()
