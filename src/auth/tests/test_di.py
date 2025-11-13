import os
from unittest.mock import AsyncMock, call, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from di import SessionManager, configure_inject, key_pair_factory, setup_di
from utils import KeyPair


@pytest.mark.asyncio
@patch("di.di.URL")
@patch("di.di.create_async_engine")
@patch("di.di.async_sessionmaker")
async def test_session_manager_lifespan(
    mock_async_sessionmaker, mock_create_async_engine, mock_url
):
    mock_sessionmaker = mock_async_sessionmaker.return_value
    mock_engine = mock_create_async_engine.return_value
    mock_dispose = AsyncMock()
    mock_engine.dispose = mock_dispose

    await SessionManager.setup()

    mock_url.create.assert_called_once_with(
        os.environ["POSTGRES_DRIVER"],
        os.environ["POSTGRES_USER"],
        os.environ["POSTGRES_PASSWORD"],
        os.environ["POSTGRES_HOST"],
        int(os.environ["POSTGRES_PORT"]),
        os.environ["POSTGRES_DB"],
    )
    mock_create_async_engine.assert_called_once_with(
        mock_url.create.return_value,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
    )
    mock_async_sessionmaker.assert_called_once_with(
        mock_create_async_engine.return_value,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    assert SessionManager.sessionmaker == mock_sessionmaker
    assert SessionManager._engine == mock_engine
    assert SessionManager._started

    await SessionManager.close()

    mock_dispose.assert_awaited_once()
    assert not SessionManager.sessionmaker
    assert not SessionManager._engine
    assert not SessionManager._started


@pytest.mark.asyncio
@patch("di.di.URL")
async def test_session_manager_setup_already_started(mock_url):
    SessionManager._started = True

    await SessionManager.setup()

    mock_url.assert_not_called()
    assert SessionManager._started


@pytest.mark.asyncio
@patch("di.di.URL")
@patch("di.di.SessionManager.close")
async def test_session_manager_setup_exception(mock_close, mock_url):
    SessionManager._started = False
    mock_url.side_effect = Exception("Details")

    with pytest.raises(Exception):
        await SessionManager.setup()

    mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_session_manager_close_already_closed():
    SessionManager._engine = None

    await SessionManager.close()

    assert not SessionManager.sessionmaker
    assert not SessionManager._engine
    assert not SessionManager._started


@pytest.mark.asyncio
@patch("di.di.SessionManager.sessionmaker")
async def test_session_factory(mock_sessionmaker):
    mock_session = mock_sessionmaker.return_value.__aenter__.return_value
    SessionManager._started = True

    async with SessionManager.session_factory() as session:
        assert session == mock_session


@pytest.mark.asyncio
async def test_session_factory_not_initialized():
    SessionManager.sessionmaker = None

    with pytest.raises(Exception) as exc_info:
        async with SessionManager.session_factory():
            pass

    assert exc_info.errisinstance(RuntimeError)
    assert exc_info.value.args == (
        "Sessionmaker not initialized; SessionManager.setup() was not called",
    )


@patch("di.di.KeyPair")
def test_key_pair_factory(mock_key_pair):
    key_pair_factory()

    mock_key_pair.assert_called_once()


@patch("di.di.inject.Binder")
@patch("di.di.SessionManager")
@patch("di.di.key_pair_factory")
def test_configure_inject(mock_key_pair_factory, mock_session_manager, mock_binder):
    configure_inject(mock_binder)

    expected_calls = [
        call(AsyncSession, mock_session_manager.session_factory),
        call(KeyPair, mock_key_pair_factory),
    ]
    mock_binder.bind_to_provider.assert_has_calls(expected_calls, any_order=True)
    assert mock_binder.bind_to_provider.call_count == 2


@pytest.mark.asyncio
@patch("di.di.SessionManager")
@patch("di.di.inject.configure")
@patch("di.di.configure_inject")
async def test_setup_di(
    mock_configure_inject, mock_inject_configure, mock_session_manager
):
    mock_session_manager.setup = AsyncMock()

    await setup_di()

    mock_session_manager.setup.assert_awaited_once()
    mock_inject_configure.assert_called_once_with(mock_configure_inject, once=True)
