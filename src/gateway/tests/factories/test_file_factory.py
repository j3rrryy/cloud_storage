from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from factories import FileFactory


@pytest.mark.asyncio
async def test_file_factory_initialize_success():
    with (
        patch("factories.file_factory.grpc.aio.insecure_channel") as mock_channel,
        patch("factories.file_factory.FileStub") as mock_stub,
        patch("factories.file_factory.FileGrpcAdapter") as mock_adapter,
    ):
        factory = FileFactory()
        mock_channel_instance = AsyncMock()
        mock_channel_instance.channel_ready = AsyncMock()
        mock_channel_instance.channel_ready.return_value = None
        mock_channel.return_value = mock_channel_instance
        mock_stub_instance = MagicMock()
        mock_stub.return_value = mock_stub_instance
        mock_adapter_instance = MagicMock()
        mock_adapter.return_value = mock_adapter_instance

        await factory.initialize()

        assert factory._file_channel == mock_channel_instance
        assert factory._file_service == mock_adapter_instance


@pytest.mark.asyncio
async def test_file_factory_initialize_exception():
    factory = FileFactory()
    with (
        patch("factories.file_factory.grpc.aio.insecure_channel") as mock_channel,
        patch.object(factory, "close", new_callable=AsyncMock) as mock_close,
    ):
        mock_channel.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            await factory.initialize()

        mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_factory_close():
    factory = FileFactory()
    mock_channel = AsyncMock()
    factory._file_channel = mock_channel

    await factory.close()

    mock_channel.close.assert_awaited_once()
    assert factory._file_channel is None
    assert factory._file_service is None


@pytest.mark.asyncio
async def test_file_factory_close_no_channel():
    factory = FileFactory()

    await factory.close()

    assert factory._file_channel is None
    assert factory._file_service is None


def test_file_factory_get_file_service():
    factory = FileFactory()
    mock_service = MagicMock()
    factory._file_service = mock_service

    result = factory.get_file_service()

    assert result == mock_service


def test_file_factory_get_file_service_not_initialized():
    factory = FileFactory()

    with pytest.raises(RuntimeError, match="FileService not initialized"):
        factory.get_file_service()
