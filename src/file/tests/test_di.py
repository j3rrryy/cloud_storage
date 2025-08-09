import os
from unittest.mock import AsyncMock, call, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from types_aiobotocore_s3 import S3Client

from di import ClientManager, configure_inject, session_factory, setup_di


@pytest.mark.asyncio
@patch("di.di.aioboto3.Session")
@patch("di.di.AioConfig")
async def test_client_manager_lifespan(mock_aioconfig, mock_session):
    mock_client = AsyncMock()
    mock_session.return_value.client.return_value = mock_client

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
        endpoint_url=f"http://{os.environ['MINIO_HOST']}:{os.environ['MINIO_PORT']}",
        aws_access_key_id=os.environ["MINIO_ROOT_USER"],
        aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"],
        config=mock_aioconfig.return_value,
    )
    assert ClientManager.client == mock_client.__aenter__.return_value
    assert ClientManager._started

    await ClientManager.close()
    assert not ClientManager.client
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
@patch("di.di.ClientManager.client")
async def test_client_factory(mock_client):
    client = ClientManager.client_factory()
    assert client == mock_client


@pytest.mark.asyncio
async def test_client_factory_exception():
    ClientManager.client = None
    with pytest.raises(Exception) as exc_info:
        ClientManager.client_factory()

    assert exc_info.errisinstance(RuntimeError)
    assert exc_info.value.args == (
        "S3Client not initialized; ClientManager.setup() was not called",
    )


@pytest.mark.asyncio
@patch("di.di.URL")
@patch("di.di.create_async_engine")
@patch("di.di.async_sessionmaker")
async def test_session_factory(
    mock_async_sessionmaker, mock_create_async_engine, mock_url
):
    mock_session = AsyncMock()
    mock_async_sessionmaker.return_value.return_value.__aenter__.return_value = (
        mock_session
    )
    session = await session_factory().__aenter__()

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
        mock_create_async_engine.return_value, class_=AsyncSession
    )
    assert session == mock_session


@patch("di.di.inject.Binder")
@patch("di.di.ClientManager")
@patch("di.di.session_factory")
def test_configure_inject(mock_session_factory, mock_client_manager, mock_binder):
    configure_inject(mock_binder)

    expected_calls = [
        call(S3Client, mock_client_manager.client_factory),
        call(AsyncSession, mock_session_factory),
    ]

    mock_binder.bind_to_provider.assert_has_calls(expected_calls, any_order=True)
    assert mock_binder.bind_to_provider.call_count == 2


@pytest.mark.asyncio
@patch("di.di.ClientManager")
@patch("di.di.inject.configure")
@patch("di.di.configure_inject")
async def test_setup_di(
    mock_configure_inject, mock_inject_configure, mock_client_manager
):
    mock_client_manager.setup = AsyncMock()
    await setup_di()

    mock_client_manager.setup.assert_awaited_once()
    mock_inject_configure.assert_called_once_with(mock_configure_inject, once=True)
