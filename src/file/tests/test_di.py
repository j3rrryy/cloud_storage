from unittest.mock import AsyncMock, call, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from types_aiobotocore_s3 import S3Client

from di import ClientManager, SessionManager, configure_inject, setup_di
from settings import Settings


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
        Settings.POSTGRES_DRIVER,
        Settings.POSTGRES_USER,
        Settings.POSTGRES_PASSWORD,
        Settings.POSTGRES_HOST,
        Settings.POSTGRES_PORT,
        Settings.POSTGRES_DB,
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
            ...

    assert exc_info.errisinstance(RuntimeError)
    assert exc_info.value.args == (
        "Sessionmaker not initialized; SessionManager.setup() was not called",
    )


@pytest.mark.asyncio
@patch("di.di.aioboto3.Session")
@patch("di.di.AioConfig")
async def test_client_manager_lifespan(mock_aioconfig, mock_session):
    mock_context = AsyncMock()
    mock_session.return_value.client.return_value = mock_context
    mock_client = AsyncMock()
    mock_context.__aenter__.return_value = mock_client

    await ClientManager.setup()

    mock_session.assert_called_once()
    mock_aioconfig.assert_called_once_with(
        connect_timeout=5,
        read_timeout=10,
        max_pool_connections=30,
        retries={"max_attempts": 3, "mode": "standard"},
        s3={"addressing_style": "path"},
    )
    mock_session.return_value.client.assert_called_once_with(
        "s3",
        use_ssl=False,
        verify=False,
        endpoint_url=f"http://{Settings.MINIO_HOST}:{Settings.MINIO_PORT}",
        aws_access_key_id=Settings.MINIO_ROOT_USER,
        aws_secret_access_key=Settings.MINIO_ROOT_PASSWORD,
        config=mock_aioconfig.return_value,
    )
    assert ClientManager.client == mock_client
    assert ClientManager._context
    assert ClientManager._started

    await ClientManager.close()

    mock_context.__aexit__.assert_awaited_once()
    assert not ClientManager.client
    assert not ClientManager._context
    assert not ClientManager._started


@pytest.mark.asyncio
@patch("di.di.aioboto3.Session")
async def test_client_manager_setup_already_started(mock_session):
    ClientManager._started = True

    await ClientManager.setup()

    mock_session.assert_not_called()
    assert ClientManager._started


@pytest.mark.asyncio
@patch("di.di.aioboto3.Session")
@patch("di.di.ClientManager.close")
async def test_client_manager_setup_exception(mock_close, mock_session):
    ClientManager._started = False
    mock_session.side_effect = Exception("Details")

    with pytest.raises(Exception):
        await ClientManager.setup()

    mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_client_manager_close_already_closed():
    ClientManager._context = None

    await ClientManager.close()

    assert not ClientManager.client
    assert not ClientManager._context
    assert not ClientManager._started


@pytest.mark.asyncio
@patch("di.di.ClientManager.client")
async def test_client_factory(mock_client):
    ClientManager._started = True

    client = ClientManager.client_factory()

    assert client == mock_client


@pytest.mark.asyncio
async def test_client_factory_not_initialized():
    ClientManager.client = None

    with pytest.raises(Exception) as exc_info:
        ClientManager.client_factory()

    assert exc_info.errisinstance(RuntimeError)
    assert exc_info.value.args == (
        "S3Client not initialized; ClientManager.setup() was not called",
    )


@patch("di.di.inject.Binder")
@patch("di.di.SessionManager")
@patch("di.di.ClientManager")
def test_configure_inject(mock_client_manager, mock_session_manager, mock_binder):
    configure_inject(mock_binder)

    expected_calls = [
        call(AsyncSession, mock_session_manager.session_factory),
        call(S3Client, mock_client_manager.client_factory),
    ]
    mock_binder.bind_to_provider.assert_has_calls(expected_calls, any_order=True)
    assert mock_binder.bind_to_provider.call_count == 2


@pytest.mark.asyncio
@patch("di.di.SessionManager")
@patch("di.di.ClientManager")
@patch("di.di.inject.configure")
@patch("di.di.configure_inject")
async def test_setup_di(
    mock_configure_inject,
    mock_inject_configure,
    mock_client_manager,
    mock_session_manager,
):
    mock_session_manager.setup = AsyncMock()
    mock_client_manager.setup = AsyncMock()

    await setup_di()

    mock_session_manager.setup.assert_awaited_once()
    mock_client_manager.setup.assert_awaited_once()
    mock_inject_configure.assert_called_once_with(mock_configure_inject, once=True)
