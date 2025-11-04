import msgspec
import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from schemas import file_schemas

from .mocks import ACCESS_TOKEN, FILE_ID, NAME, SIZE, TIMESTAMP, URL

PREFIX = "/api/v1/file"


@pytest.mark.asyncio
async def test_upload_file(client):
    data = file_schemas.UploadFile(NAME, SIZE)
    response = await client.post(
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
async def test_file_info(client):
    response = await client.get(
        f"{PREFIX}/file-info/{FILE_ID}",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {
        "file_id": FILE_ID,
        "name": NAME,
        "size": SIZE,
        "uploaded_at": TIMESTAMP.isoformat(),
    }


@pytest.mark.asyncio
async def test_file_list(client):
    response = await client.get(
        f"{PREFIX}/file-list", headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {
        "files": [
            {
                "file_id": FILE_ID,
                "name": NAME,
                "size": SIZE,
                "uploaded_at": TIMESTAMP.isoformat(),
            }
        ]
    }


@pytest.mark.asyncio
async def test_download_file(client):
    response = await client.get(
        f"{PREFIX}/download-file/{FILE_ID}",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        follow_redirects=False,
    )
    assert response.has_redirect_location


@pytest.mark.asyncio
async def test_delete_files(client):
    response = await client.delete(
        f"{PREFIX}/delete-files",
        params={"file_id": (FILE_ID,)},
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_all_files(client):
    response = await client.delete(
        f"{PREFIX}/delete-all-files",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    assert response.status_code == HTTP_204_NO_CONTENT
