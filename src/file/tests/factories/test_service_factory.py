from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from factories import ServiceFactory


@pytest.mark.asyncio
async def test_service_factory_initialize_success():
    service_factory = ServiceFactory()

    with (
        patch.object(
            service_factory._file_repository_factory,
            "initialize",
            new_callable=AsyncMock,
        ) as mock_repository_init,
        patch.object(
            service_factory._file_storage_factory, "initialize", new_callable=AsyncMock
        ) as mock_storage_init,
        patch.object(
            service_factory._cache_factory, "initialize", new_callable=AsyncMock
        ) as mock_cache_init,
    ):
        await service_factory.initialize()

        mock_repository_init.assert_awaited_once()
        mock_storage_init.assert_awaited_once()
        mock_cache_init.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_factory_initialize_exception():
    service_factory = ServiceFactory()
    with (
        patch.object(
            service_factory._file_repository_factory,
            "initialize",
            new_callable=AsyncMock,
        ) as mock_repository_init,
        patch.object(
            service_factory._file_storage_factory, "initialize", new_callable=AsyncMock
        ),
        patch.object(
            service_factory._cache_factory, "initialize", new_callable=AsyncMock
        ),
        patch.object(service_factory, "close", new_callable=AsyncMock) as mock_close,
    ):
        mock_repository_init.side_effect = Exception("Initialization failed")

        with pytest.raises(Exception):
            await service_factory.initialize()

        mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_factory_close():
    service_factory = ServiceFactory()

    with (
        patch.object(
            service_factory._file_repository_factory, "close", new_callable=AsyncMock
        ) as mock_repository_close,
        patch.object(
            service_factory._file_storage_factory, "close", new_callable=AsyncMock
        ) as mock_storage_close,
        patch.object(
            service_factory._cache_factory, "close", new_callable=AsyncMock
        ) as mock_cache_close,
    ):
        await service_factory.close()

        mock_repository_close.assert_awaited_once()
        mock_storage_close.assert_awaited_once()
        mock_cache_close.assert_awaited_once()


def test_service_factory_get_file_repository():
    service_factory = ServiceFactory()
    mock_repository = MagicMock()

    with patch.object(
        service_factory._file_repository_factory,
        "get_file_repository",
        return_value=mock_repository,
    ) as mock_get:
        result = service_factory.get_file_repository()

        assert result == mock_repository
        mock_get.assert_called_once()


def test_service_factory_get_file_storage():
    service_factory = ServiceFactory()
    mock_storage = MagicMock()

    with patch.object(
        service_factory._file_storage_factory,
        "get_file_storage",
        return_value=mock_storage,
    ) as mock_get:
        result = service_factory.get_file_storage()

        assert result == mock_storage
        mock_get.assert_called_once()


def test_service_factory_get_cache():
    service_factory = ServiceFactory()
    mock_cache = MagicMock()

    with patch.object(
        service_factory._cache_factory, "get_cache", return_value=mock_cache
    ) as mock_get:
        result = service_factory.get_cache()

        assert result == mock_cache
        mock_get.assert_called_once()


def test_service_factory_get_file_controller():
    service_factory = ServiceFactory()
    mock_file_service = MagicMock()
    mock_file_controller = MagicMock()

    with (
        patch.object(service_factory, "get_file_repository"),
        patch.object(service_factory, "get_file_storage"),
        patch.object(service_factory, "get_cache"),
        patch("factories.service_factory.FileService", return_value=mock_file_service),
        patch(
            "factories.service_factory.FileController",
            return_value=mock_file_controller,
        ) as mock_file_controller_class,
    ):
        result = service_factory.get_file_controller()

        assert result == mock_file_controller
        mock_file_controller_class.assert_called_once_with(mock_file_service)


def test_service_factory_get_file_controller_cached():
    service_factory = ServiceFactory()
    mock_controller = MagicMock()
    service_factory._file_controller = mock_controller

    result = service_factory.get_file_controller()

    assert result == mock_controller


@pytest.mark.asyncio
async def test_service_factory_get_is_ready():
    service_factory = ServiceFactory()

    is_ready = await service_factory.get_is_ready()()

    assert not is_ready


@pytest.mark.asyncio
async def test_service_factory_get_is_ready_exception():
    service_factory = ServiceFactory()
    mock_is_ready = MagicMock()
    mock_is_ready.side_effect = Exception("Healthcheck timeout")
    service_factory._file_repository_factory.is_ready = mock_is_ready

    is_ready = await service_factory.get_is_ready()()

    assert not is_ready
