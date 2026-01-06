from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from factories import AuthRepositoryFactory


@pytest.mark.asyncio
async def test_auth_repository_factory_initialize_success():
    with (
        patch(
            "factories.auth_repository_factory.create_async_engine"
        ) as mock_engine_factory,
        patch("factories.auth_repository_factory.AuthRepository") as mock_repository,
    ):
        factory = AuthRepositoryFactory()
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        mock_repository_instance = MagicMock()
        mock_repository.return_value = mock_repository_instance

        await factory.initialize()

        assert factory._engine == mock_engine
        assert factory._auth_repository == mock_repository_instance


@pytest.mark.asyncio
async def test_auth_repository_factory_initialize_exception():
    factory = AuthRepositoryFactory()
    with (
        patch(
            "factories.auth_repository_factory.create_async_engine"
        ) as mock_engine_factory,
        patch.object(factory, "close", new_callable=AsyncMock) as mock_close,
    ):
        mock_engine_factory.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            await factory.initialize()

        mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_auth_repository_factory_close():
    factory = AuthRepositoryFactory()
    mock_engine = AsyncMock()
    factory._engine = mock_engine

    await factory.close()

    mock_engine.dispose.assert_awaited_once()
    assert factory._engine is None
    assert factory._auth_repository is None


@pytest.mark.asyncio
async def test_auth_repository_factory_close_no_engine():
    factory = AuthRepositoryFactory()

    await factory.close()

    assert factory._engine is None
    assert factory._auth_repository is None


def test_auth_repository_factory_get_auth_repository():
    factory = AuthRepositoryFactory()
    mock_repository = MagicMock()
    factory._auth_repository = mock_repository

    result = factory.get_auth_repository()

    assert result == mock_repository


def test_auth_repository_factory_get_auth_repository_not_initialized():
    factory = AuthRepositoryFactory()

    with pytest.raises(RuntimeError, match="AuthRepository not initialized"):
        factory.get_auth_repository()
