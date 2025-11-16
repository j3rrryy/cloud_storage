from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from factories import AuthFactory


@pytest.mark.asyncio
async def test_auth_factory_initialize_success():
    with (
        patch("factories.auth_factory.grpc.aio.insecure_channel") as mock_channel,
        patch("factories.auth_factory.AuthStub") as mock_stub,
        patch("factories.auth_factory.AuthGrpcAdapter") as mock_adapter,
    ):
        factory = AuthFactory()
        mock_channel_instance = AsyncMock()
        mock_channel_instance.channel_ready = AsyncMock()
        mock_channel_instance.channel_ready.return_value = None
        mock_channel.return_value = mock_channel_instance
        mock_stub_instance = MagicMock()
        mock_stub.return_value = mock_stub_instance
        mock_adapter_instance = MagicMock()
        mock_adapter.return_value = mock_adapter_instance

        await factory.initialize()

        assert factory._auth_channel == mock_channel_instance
        assert factory._auth_service == mock_adapter_instance


@pytest.mark.asyncio
async def test_auth_factory_initialize_exception():
    factory = AuthFactory()
    with (
        patch("factories.auth_factory.grpc.aio.insecure_channel") as mock_channel,
        patch.object(factory, "close", new_callable=AsyncMock) as mock_close,
    ):
        mock_channel.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            await factory.initialize()

        mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_auth_factory_close():
    factory = AuthFactory()
    mock_channel = AsyncMock()
    factory._auth_channel = mock_channel

    await factory.close()

    mock_channel.close.assert_awaited_once()
    assert factory._auth_channel is None
    assert factory._auth_service is None


@pytest.mark.asyncio
async def test_auth_factory_close_no_channel():
    factory = AuthFactory()

    await factory.close()

    assert factory._auth_channel is None
    assert factory._auth_service is None


def test_auth_factory_get_auth_service():
    factory = AuthFactory()
    mock_service = MagicMock()
    factory._auth_service = mock_service

    result = factory.get_auth_service()

    assert result == mock_service


def test_auth_factory_get_auth_service_not_initialized():
    factory = AuthFactory()

    with pytest.raises(RuntimeError, match="AuthService not initialized"):
        factory.get_auth_service()
