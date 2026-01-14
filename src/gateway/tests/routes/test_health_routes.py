import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE

PREFIX = "/api/health"


@pytest.mark.asyncio
async def test_live(client):
    response = await client.get(f"{PREFIX}/live")

    assert response.status_code == HTTP_200_OK


@pytest.mark.asyncio
async def test_ready(client):
    response = await client.get(f"{PREFIX}/ready")

    assert response.status_code == HTTP_200_OK


@pytest.mark.asyncio
async def test_ready_not_ready(is_ready, client):
    is_ready.return_value = False

    response = await client.get(f"{PREFIX}/ready")

    assert response.status_code == HTTP_503_SERVICE_UNAVAILABLE
