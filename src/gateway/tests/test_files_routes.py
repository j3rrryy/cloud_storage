import msgspec
import pytest
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_403_FORBIDDEN,
)
from litestar.testing import AsyncTestClient

from schemas import files

from .mocks import ACCESS_TOKEN, FILE_ID, NAME, PATH, SIZE, TIMESTAMP, URL

PREFIX = "/api/v1/files"


@pytest.mark.asyncio
async def test_upload_file(verified_client: AsyncTestClient):
    data = files.UploadFile(NAME, PATH, SIZE)
    response = await verified_client.post(
        f"{PREFIX}/upload-file",
        content=msgspec.msgpack.encode(data),
        headers={
            "Content-Type": "application/msgpack",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_201_CREATED
    assert response_data == {"url": URL}


@pytest.mark.asyncio
async def test_unverified_upload_file(unverified_client: AsyncTestClient):
    data = files.UploadFile(NAME, PATH, SIZE)
    response = await unverified_client.post(
        f"{PREFIX}/upload-file",
        content=msgspec.msgpack.encode(data),
        headers={
            "Content-Type": "application/msgpack",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json() == {"status_code": 403, "detail": "Email not verified"}


@pytest.mark.asyncio
async def test_file_info(verified_client: AsyncTestClient):
    response = await verified_client.get(
        f"{PREFIX}/file-info/{FILE_ID}",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {
        "file_id": FILE_ID,
        "name": NAME,
        "path": PATH,
        "size": str(SIZE),
        "uploaded": TIMESTAMP,
    }


@pytest.mark.asyncio
async def test_unverified_file_info(unverified_client: AsyncTestClient):
    response = await unverified_client.get(
        f"{PREFIX}/file-info/{FILE_ID}",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json() == {"status_code": 403, "detail": "Email not verified"}


@pytest.mark.asyncio
async def test_file_list(verified_client: AsyncTestClient):
    response = await verified_client.get(
        f"{PREFIX}/file-list", headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {
        "files": [
            {
                "file_id": FILE_ID,
                "name": NAME,
                "path": PATH,
                "size": str(SIZE),
                "uploaded": TIMESTAMP,
            }
        ]
    }


@pytest.mark.asyncio
async def test_unverified_file_list(unverified_client: AsyncTestClient):
    response = await unverified_client.get(
        f"{PREFIX}/file-list", headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json() == {"status_code": 403, "detail": "Email not verified"}


@pytest.mark.asyncio
async def test_download_file(verified_client: AsyncTestClient):
    response = await verified_client.get(
        f"{PREFIX}/download-file/{FILE_ID}",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        follow_redirects=False,
    )
    assert response.has_redirect_location


@pytest.mark.asyncio
async def test_unverified_download_file(unverified_client: AsyncTestClient):
    response = await unverified_client.get(
        f"{PREFIX}/download-file/{FILE_ID}",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        follow_redirects=False,
    )
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json() == {"status_code": 403, "detail": "Email not verified"}


@pytest.mark.asyncio
async def test_delete_files(verified_client: AsyncTestClient):
    response = await verified_client.delete(
        f"{PREFIX}/delete-files",
        params={"file_id": (FILE_ID,)},
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_unverified_delete_files(unverified_client: AsyncTestClient):
    response = await unverified_client.delete(
        f"{PREFIX}/delete-files",
        params={"file_id": (FILE_ID,)},
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json() == {"status_code": 403, "detail": "Email not verified"}


@pytest.mark.asyncio
async def test_delete_all_files(verified_client: AsyncTestClient):
    response = await verified_client.delete(
        f"{PREFIX}/delete-all-files",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_unverified_delete_all_files(unverified_client: AsyncTestClient):
    response = await unverified_client.delete(
        f"{PREFIX}/delete-all-files",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json() == {"status_code": 403, "detail": "Email not verified"}
