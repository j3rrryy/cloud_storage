from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from factories import FileRepositoryFactory


@pytest.mark.asyncio
async def test_file_repository_factory_initialize_success():
    with (
        patch(
            "factories.file_repository_factory.create_async_engine"
        ) as mock_engine_factory,
        patch("factories.file_repository_factory.FileRepository") as mock_repository,
    ):
        factory = FileRepositoryFactory()
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        mock_repository_instance = MagicMock()
        mock_repository.return_value = mock_repository_instance

        await factory.initialize()

        assert factory._engine == mock_engine
        assert factory._file_repository == mock_repository_instance


@pytest.mark.asyncio
async def test_file_repository_factory_initialize_exception():
    factory = FileRepositoryFactory()
    with (
        patch(
            "factories.file_repository_factory.create_async_engine"
        ) as mock_engine_factory,
        patch.object(factory, "close", new_callable=AsyncMock) as mock_close,
    ):
        mock_engine_factory.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            await factory.initialize()

        mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_repository_factory_close():
    factory = FileRepositoryFactory()
    mock_engine = AsyncMock()
    factory._engine = mock_engine

    await factory.close()

    mock_engine.dispose.assert_awaited_once()
    assert factory._engine is None
    assert factory._file_repository is None


@pytest.mark.asyncio
async def test_file_repository_factory_close_no_engine():
    factory = FileRepositoryFactory()

    await factory.close()

    assert factory._engine is None
    assert factory._file_repository is None


def test_file_repository_factory_get_file_repository():
    factory = FileRepositoryFactory()
    mock_repository = MagicMock()
    factory._file_repository = mock_repository

    result = factory.get_file_repository()

    assert result == mock_repository


def test_file_repository_factory_get_file_repository_not_initialized():
    factory = FileRepositoryFactory()

    with pytest.raises(RuntimeError, match="FileRepository not initialized"):
        factory.get_file_repository()


@pytest.mark.asyncio
async def test_file_repository_factory_is_ready_success():
    factory = FileRepositoryFactory()
    factory._engine = MagicMock()
    factory._engine.__aenter__ = AsyncMock()
    factory._file_repository = AsyncMock()

    is_ready = await factory.is_ready()

    assert is_ready


@pytest.mark.asyncio
async def test_file_repository_factory_is_ready_fail():
    factory = FileRepositoryFactory()
    factory._engine = MagicMock()
    factory._file_repository = AsyncMock()
    factory._engine.connect.side_effect = Exception("Connection failed")

    is_ready = await factory.is_ready()

    assert not is_ready


@pytest.mark.asyncio
async def test_file_repository_factory_is_ready_not_initialized():
    factory = FileRepositoryFactory()

    is_ready = await factory.is_ready()

    assert not is_ready
