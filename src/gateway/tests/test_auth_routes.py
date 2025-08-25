import msgspec
import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from schemas import auth_schemas

from .mocks import (
    ACCESS_TOKEN,
    BROWSER,
    CODE,
    EMAIL,
    PASSWORD,
    REFRESH_TOKEN,
    SESSION_ID,
    TIMESTAMP,
    USER_ID,
    USER_IP,
    USERNAME,
    VERIFICATION_TOKEN,
)

PREFIX = "/api/v1/auth"


@pytest.mark.asyncio
async def test_register(client):
    data = auth_schemas.Registration(USERNAME, EMAIL, PASSWORD)
    response = await client.post(
        f"{PREFIX}/register",
        content=msgspec.msgpack.encode(data),
        headers={"Content-Type": "application/msgpack"},
    )
    assert response.status_code == HTTP_201_CREATED


@pytest.mark.asyncio
async def test_verify_email(client):
    response = await client.get(
        f"{PREFIX}/verify-email", params={"verification_token": VERIFICATION_TOKEN}
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_request_reset(client):
    data = auth_schemas.ForgotPassword(EMAIL)
    response = await client.post(
        f"{PREFIX}/request-reset-code",
        content=msgspec.msgpack.encode(data),
        headers={"Content-Type": "application/msgpack"},
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {"user_id": USER_ID}


@pytest.mark.asyncio
async def test_validate_reset_code(client):
    data = auth_schemas.ResetCode(USER_ID, CODE)
    response = await client.post(
        f"{PREFIX}/validate-reset-code",
        content=msgspec.msgpack.encode(data),
        headers={"Content-Type": "application/msgpack"},
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {"is_valid": True}


@pytest.mark.asyncio
async def test_reset_password(client):
    data = auth_schemas.ResetPassword(USER_ID, PASSWORD)
    response = await client.post(
        f"{PREFIX}/reset-password",
        content=msgspec.msgpack.encode(data),
        headers={"Content-Type": "application/msgpack"},
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_log_in(client):
    data = auth_schemas.LogIn(USERNAME, PASSWORD)
    response = await client.post(
        f"{PREFIX}/log-in",
        content=msgspec.msgpack.encode(data),
        headers={"Content-Type": "application/msgpack"},
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {
        "access_token": ACCESS_TOKEN,
        "refresh_token": REFRESH_TOKEN,
    }


@pytest.mark.asyncio
async def test_log_out(client):
    response = await client.post(
        f"{PREFIX}/log-out", headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_resend_verification_mail(client):
    response = await client.post(
        f"{PREFIX}/resend-verification-mail",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_auth(client):
    response = await client.get(
        f"{PREFIX}/auth", headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {"user_id": USER_ID}


@pytest.mark.asyncio
async def test_refresh(client):
    data = auth_schemas.RefreshToken(REFRESH_TOKEN)
    response = await client.post(
        f"{PREFIX}/refresh",
        content=msgspec.msgpack.encode(data),
        headers={
            "Content-Type": "application/msgpack",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_201_CREATED
    assert response_data == {
        "access_token": ACCESS_TOKEN,
        "refresh_token": REFRESH_TOKEN,
    }


@pytest.mark.asyncio
async def test_session_list(client):
    response = await client.get(
        f"{PREFIX}/session-list", headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {
        "sessions": [
            {
                "session_id": SESSION_ID,
                "user_ip": USER_IP,
                "browser": BROWSER,
                "created_at": TIMESTAMP.isoformat(),
            }
        ]
    }


@pytest.mark.asyncio
async def test_revoke_session(client):
    data = auth_schemas.SessionId(SESSION_ID)
    response = await client.post(
        f"{PREFIX}/revoke-session",
        content=msgspec.msgpack.encode(data),
        headers={
            "Content-Type": "application/msgpack",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_profile(client):
    response = await client.get(
        f"{PREFIX}/profile", headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {
        "user_id": USER_ID,
        "username": USERNAME,
        "email": EMAIL,
        "registered_at": TIMESTAMP.isoformat(),
        "verified": True,
    }


@pytest.mark.asyncio
async def test_update_email(client):
    data = auth_schemas.UpdateEmail(EMAIL)
    response = await client.patch(
        f"{PREFIX}/update-email",
        content=msgspec.msgpack.encode(data),
        headers={
            "Content-Type": "application/msgpack",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_update_password(client):
    data = auth_schemas.UpdatePassword(PASSWORD, PASSWORD)
    response = await client.patch(
        f"{PREFIX}/update-password",
        content=msgspec.msgpack.encode(data),
        headers={
            "Content-Type": "application/msgpack",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_profile(client):
    response = await client.delete(
        f"{PREFIX}/delete-profile", headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    assert response.status_code == HTTP_204_NO_CONTENT
