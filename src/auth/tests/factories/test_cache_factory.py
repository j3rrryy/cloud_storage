from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from factories import CacheFactory


@pytest.mark.asyncio
async def test_cache_factory_initialize_success():
    with patch("factories.cache_factory.Cache") as mock_cache:
        factory = CacheFactory()
        mock_cache_instance = AsyncMock()
        mock_cache.return_value = mock_cache_instance

        await factory.initialize()

        mock_cache_instance.setup.assert_called_once()
        assert factory._cache == mock_cache.return_value


@pytest.mark.asyncio
async def test_cache_factory_initialize_exception():
    factory = CacheFactory()
    with (
        patch("factories.cache_factory.Cache") as mock_cache,
        patch.object(factory, "close", new_callable=AsyncMock) as mock_close,
    ):
        mock_cache.return_value.setup.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            await factory.initialize()

        mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_cache_factory_close():
    factory = CacheFactory()
    mock_cache = AsyncMock()
    factory._cache = mock_cache

    await factory.close()

    mock_cache.close.assert_awaited_once()
    assert factory._cache is None


@pytest.mark.asyncio
async def test_cache_factory_close_no_cache():
    factory = CacheFactory()

    await factory.close()

    assert factory._cache is None


def test_cache_factory_get_cache():
    factory = CacheFactory()
    mock_cache = MagicMock()
    factory._cache = mock_cache

    result = factory.get_cache()

    assert result == mock_cache


def test_cache_factory_get_cache_not_initialized():
    factory = CacheFactory()

    with pytest.raises(RuntimeError, match="RedisCache not initialized"):
        factory.get_cache()


@pytest.mark.asyncio
async def test_cache_factory_is_ready_success():
    factory = CacheFactory()
    factory._cache = AsyncMock()

    is_ready = await factory.is_ready()

    assert is_ready


@pytest.mark.asyncio
async def test_cache_factory_is_ready_fail():
    factory = CacheFactory()
    factory._cache = AsyncMock()
    factory._cache.ping.side_effect = Exception("Connection failed")

    is_ready = await factory.is_ready()

    assert not is_ready


@pytest.mark.asyncio
async def test_cache_factory_is_ready_not_initialized():
    factory = CacheFactory()

    is_ready = await factory.is_ready()

    assert not is_ready
