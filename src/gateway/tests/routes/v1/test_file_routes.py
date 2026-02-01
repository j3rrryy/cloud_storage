import msgspec
import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from schemas import file_schemas

from ...mocks import ACCESS_TOKEN, ETAG, FILE_ID, NAME, SIZE, TIMESTAMP, UPLOAD_ID, URL

PREFIX = "/api/v1/files"


@pytest.mark.asyncio
async def test_initiate_upload(client):
    data = file_schemas.InitiateUpload(NAME, SIZE)

    response = await client.post(
        f"{PREFIX}/upload/initiate",
        content=msgspec.msgpack.encode(data),
        headers={
            "Content-Type": "application/msgpack",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {
        "upload_id": UPLOAD_ID,
        "part_size": SIZE,
        "parts": [{"part_number": 1, "url": URL}],
    }


@pytest.mark.asyncio
async def test_complete_upload(client):
    data = file_schemas.CompleteUpload(UPLOAD_ID, [file_schemas.CompletePart(1, ETAG)])

    response = await client.post(
        f"{PREFIX}/upload/complete",
        content=msgspec.msgpack.encode(data),
        headers={
            "Content-Type": "application/msgpack",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
    )

    assert response.status_code == HTTP_201_CREATED


@pytest.mark.asyncio
async def test_abort_upload(client):
    response = await client.delete(
        f"{PREFIX}/upload/{UPLOAD_ID}/abort",
        headers={
            "Content-Type": "application/msgpack",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
    )

    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_file_list(client):
    response = await client.get(
        f"{PREFIX}", headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
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
async def test_download(client):
    response = await client.get(
        f"{PREFIX}/download/{FILE_ID}",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        follow_redirects=False,
    )

    assert response.has_redirect_location


@pytest.mark.asyncio
async def test_delete(client):
    response = await client.delete(
        f"{PREFIX}",
        params={"file_id": (FILE_ID,)},
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )

    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_all(client):
    response = await client.delete(
        f"{PREFIX}/all",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )

    assert response.status_code == HTTP_204_NO_CONTENT
