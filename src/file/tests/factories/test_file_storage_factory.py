from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from factories import FileStorageFactory


@pytest.mark.asyncio
async def test_file_storage_factory_initialize_success():
    with (
        patch("factories.file_storage_factory.aioboto3.Session") as mock_session,
        patch("factories.file_storage_factory.FileStorage") as mock_storage,
    ):
        factory = FileStorageFactory()
        mock_context = MagicMock()
        mock_session.return_value.client.return_value = mock_context
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance

        await factory.initialize()

        mock_context.__aenter__.assert_awaited_once()
        assert factory._context == mock_context
        assert factory._file_storage == mock_storage_instance


@pytest.mark.asyncio
async def test_file_storage_factory_initialize_exception():
    factory = FileStorageFactory()
    with (
        patch("factories.file_storage_factory.aioboto3.Session") as mock_session,
        patch.object(factory, "close", new_callable=AsyncMock) as mock_close,
    ):
        mock_session.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            await factory.initialize()

        mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_storage_factory_close():
    factory = FileStorageFactory()
    mock_context = AsyncMock()
    factory._context = mock_context

    await factory.close()

    mock_context.__aexit__.assert_awaited_once()
    assert factory._context is None
    assert factory._file_storage is None


@pytest.mark.asyncio
async def test_file_storage_factory_close_no_context():
    factory = FileStorageFactory()

    await factory.close()

    assert factory._context is None
    assert factory._file_storage is None


def test_file_storage_factory_get_file_storage():
    factory = FileStorageFactory()
    mock_storage = MagicMock()
    factory._file_storage = mock_storage

    result = factory.get_file_storage()

    assert result == mock_storage


def test_file_storage_factory_get_file_storage_not_initialized():
    factory = FileStorageFactory()

    with pytest.raises(RuntimeError, match="FileStorage not initialized"):
        factory.get_file_storage()


@pytest.mark.asyncio
async def test_file_storage_factory_is_ready_success():
    factory = FileStorageFactory()
    factory._context = MagicMock()
    factory._file_storage = AsyncMock()

    is_ready = await factory.is_ready()

    assert is_ready


@pytest.mark.asyncio
async def test_file_storage_factory_is_ready_fail():
    factory = FileStorageFactory()
    factory._context = MagicMock()
    factory._file_storage = AsyncMock()
    factory._file_storage.ping.side_effect = Exception("Connection failed")

    is_ready = await factory.is_ready()

    assert not is_ready


@pytest.mark.asyncio
async def test_file_storage_factory_is_ready_not_initialized():
    factory = FileStorageFactory()

    is_ready = await factory.is_ready()

    assert not is_ready
