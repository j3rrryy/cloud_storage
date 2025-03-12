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
    create_database_crud,
    create_storage_crud,
)


@pytest.mark.asyncio
async def test_upload_file(file_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.storage.CRUD", new_callable=create_storage_crud),
        patch("controllers.database.cache", new_callable=create_cache),
    ):
        request = pb2.UploadFileRequest(
            user_id=USER_ID, name=NAME, path=PATH, size=SIZE
        )
        response = await file_servicer.UploadFile(request, MagicMock(ServicerContext))
        assert response == pb2.FileURLResponse(url=RELATIVE_URL)


@pytest.mark.asyncio
async def test_file_info(file_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.cache", new_callable=create_cache),
    ):
        request = pb2.FileOperationRequest(user_id=USER_ID, file_id=FILE_ID)
        response = await file_servicer.FileInfo(request, MagicMock(ServicerContext))
        assert response == pb2.FileInfoResponse(
            file_id=FILE_ID,
            name=NAME,
            path=PATH,
            size=SIZE,
            uploaded=Timestamp(seconds=int(TIMESTAMP.timestamp())),
        )


@pytest.mark.asyncio
async def test_file_list(file_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.database.cache", new_callable=create_cache),
    ):
        request = pb2.UserId(user_id=USER_ID)
        response = await file_servicer.FileList(request, MagicMock(ServicerContext))
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
async def test_download_file(file_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.storage.CRUD", new_callable=create_storage_crud),
        patch("controllers.database.cache", new_callable=create_cache),
    ):
        request = pb2.FileOperationRequest(user_id=USER_ID, file_id=FILE_ID)
        response = await file_servicer.DownloadFile(request, MagicMock(ServicerContext))
        assert response == pb2.FileURLResponse(url=RELATIVE_URL)


@pytest.mark.asyncio
async def test_delete_files(file_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.storage.CRUD", new_callable=create_storage_crud),
        patch("controllers.database.cache", new_callable=create_cache),
    ):
        request = pb2.DeleteFilesRequest(user_id=USER_ID, file_ids=(FILE_ID,))
        response = await file_servicer.DeleteFiles(request, MagicMock(ServicerContext))
        assert response == Empty()


@pytest.mark.asyncio
async def test_delete_all_files(file_servicer):
    with (
        patch("controllers.database.CRUD", new_callable=create_database_crud),
        patch("controllers.storage.CRUD", new_callable=create_storage_crud),
        patch("controllers.database.cache", new_callable=create_cache),
    ):
        request = pb2.UserId(user_id=USER_ID)
        response = await file_servicer.DeleteAllFiles(
            request, MagicMock(ServicerContext)
        )
        assert response == Empty()
