import msgspec
import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from litestar.testing import AsyncTestClient

from schemas import auth

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
async def test_register(verified_client: AsyncTestClient):
    data = auth.Registration(USERNAME, EMAIL, PASSWORD)
    response = await verified_client.post(
        f"{PREFIX}/register",
        content=msgspec.msgpack.encode(data),
        headers={"Content-Type": "application/msgpack"},
    )
    assert response.status_code == HTTP_201_CREATED


@pytest.mark.asyncio
async def test_verify_email(verified_client: AsyncTestClient):
    response = await verified_client.get(
        f"{PREFIX}/verify-email", params={"verification_token": VERIFICATION_TOKEN}
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_request_reset(verified_client: AsyncTestClient):
    data = auth.ForgotPassword(EMAIL)
    response = await verified_client.post(
        f"{PREFIX}/request-reset-code",
        content=msgspec.msgpack.encode(data),
        headers={"Content-Type": "application/msgpack"},
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {"user_id": USER_ID}


@pytest.mark.asyncio
async def test_validate_reset_code(verified_client: AsyncTestClient):
    data = auth.ResetCode(USER_ID, CODE)
    response = await verified_client.post(
        f"{PREFIX}/validate-reset-code",
        content=msgspec.msgpack.encode(data),
        headers={"Content-Type": "application/msgpack"},
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {"is_valid": True}


@pytest.mark.asyncio
async def test_reset_password(verified_client: AsyncTestClient):
    data = auth.ResetPassword(USER_ID, PASSWORD)
    response = await verified_client.post(
        f"{PREFIX}/reset-password",
        content=msgspec.msgpack.encode(data),
        headers={"Content-Type": "application/msgpack"},
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_log_in(verified_client: AsyncTestClient):
    data = auth.LogIn(USERNAME, PASSWORD)
    response = await verified_client.post(
        f"{PREFIX}/log-in",
        content=msgspec.msgpack.encode(data),
        headers={"Content-Type": "application/msgpack"},
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {
        "access_token": ACCESS_TOKEN,
        "refresh_token": REFRESH_TOKEN,
        "token_type": "bearer",
    }


@pytest.mark.asyncio
async def test_unverified_log_in(unverified_client: AsyncTestClient):
    data = auth.LogIn(USERNAME, PASSWORD)
    response = await unverified_client.post(
        f"{PREFIX}/log-in",
        content=msgspec.msgpack.encode(data),
        headers={"Content-Type": "application/msgpack"},
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {
        "access_token": ACCESS_TOKEN,
        "refresh_token": REFRESH_TOKEN,
        "token_type": "bearer",
    }


@pytest.mark.asyncio
async def test_log_out(verified_client: AsyncTestClient):
    response = await verified_client.post(
        f"{PREFIX}/log-out", headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_resend_verification_mail(verified_client: AsyncTestClient):
    response = await verified_client.post(
        f"{PREFIX}/resend-verification-mail",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_auth(verified_client: AsyncTestClient):
    response = await verified_client.get(
        f"{PREFIX}/auth", headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {"user_id": USER_ID, "verified": True}


@pytest.mark.asyncio
async def test_refresh(verified_client: AsyncTestClient):
    data = auth.RefreshToken(REFRESH_TOKEN)
    response = await verified_client.post(
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
        "token_type": "bearer",
    }


@pytest.mark.asyncio
async def test_session_list(verified_client: AsyncTestClient):
    response = await verified_client.get(
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
                "last_accessed": TIMESTAMP,
            }
        ]
    }


@pytest.mark.asyncio
async def test_revoke_session(verified_client: AsyncTestClient):
    data = auth.SessionId(SESSION_ID)
    response = await verified_client.post(
        f"{PREFIX}/revoke-session",
        content=msgspec.msgpack.encode(data),
        headers={
            "Content-Type": "application/msgpack",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_profile(verified_client: AsyncTestClient):
    response = await verified_client.get(
        f"{PREFIX}/profile", headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )

    response_data = msgspec.msgpack.decode(response.content)
    assert response.status_code == HTTP_200_OK
    assert response_data == {
        "user_id": USER_ID,
        "username": USERNAME,
        "email": EMAIL,
        "registered": TIMESTAMP,
        "verified": True,
    }


@pytest.mark.asyncio
async def test_update_email(verified_client: AsyncTestClient):
    data = auth.UpdateEmail(EMAIL)
    response = await verified_client.patch(
        f"{PREFIX}/update-email",
        content=msgspec.msgpack.encode(data),
        headers={
            "Content-Type": "application/msgpack",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_update_password(verified_client: AsyncTestClient):
    data = auth.UpdatePassword(PASSWORD, PASSWORD)
    response = await verified_client.patch(
        f"{PREFIX}/update-password",
        content=msgspec.msgpack.encode(data),
        headers={
            "Content-Type": "application/msgpack",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
    )
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_profile(verified_client: AsyncTestClient):
    response = await verified_client.delete(
        f"{PREFIX}/delete-profile", headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    assert response.status_code == HTTP_204_NO_CONTENT
