import pytest

from services import Files

from .mocks import FILE_ID, NAME, PATH, SIZE, TIMESTAMP, URL, USER_ID


@pytest.mark.asyncio
async def test_upload_file(files_service: Files):
    data = {"user_id": USER_ID, "name": NAME, "path": PATH, "size": SIZE}
    response = await files_service.upload_file(data)
    assert response == URL


@pytest.mark.asyncio
async def test_file_info(files_service: Files):
    data = {"user_id": USER_ID, "file_id": FILE_ID}
    response = await files_service.file_info(data)
    assert response["file_id"] == FILE_ID
    assert response["name"] == NAME
    assert response["path"] == PATH
    assert response["size"] == str(SIZE)
    assert response["uploaded"] == TIMESTAMP


@pytest.mark.asyncio
async def test_file_list(files_service: Files):
    response = await files_service.file_list(USER_ID)
    first_file = next(response)
    assert first_file["file_id"] == FILE_ID
    assert first_file["name"] == NAME
    assert first_file["path"] == PATH
    assert first_file["size"] == str(SIZE)
    assert first_file["uploaded"] == TIMESTAMP


@pytest.mark.asyncio
async def test_download_file(files_service: Files):
    data = {"user_id": USER_ID, "file_id": FILE_ID}
    response = await files_service.download_file(data)
    assert response == URL


@pytest.mark.asyncio
async def test_delete_files(files_service: Files):
    data = {"user_id": USER_ID, "file_ids": (FILE_ID,)}
    response = await files_service.delete_files(data)
    assert response is None


@pytest.mark.asyncio
async def test_delete_all_files(files_service: Files):
    response = await files_service.delete_all_files(USER_ID)
    assert response is None
