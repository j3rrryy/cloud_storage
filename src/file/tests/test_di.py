import os
from unittest.mock import call, patch

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from types_aiobotocore_s3 import S3Client

from di import client_factory, configure_inject, sessionmaker_factory, setup_di


@patch("di.di.URL")
@patch("di.di.create_async_engine")
@patch("di.di.async_sessionmaker")
def test_sessionmaker_factory(
    mock_async_sessionmaker, mock_create_async_engine, mock_url
):
    sessionmaker = sessionmaker_factory()
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
        pool_size=10,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
    )
    mock_async_sessionmaker.assert_called_once_with(
        mock_create_async_engine.return_value, class_=AsyncSession
    )
    assert sessionmaker == mock_async_sessionmaker.return_value


@patch("di.di.session")
@patch("di.di.config")
def test_client_factory(mock_config, mock_session):
    client = client_factory()
    mock_session.get_session.assert_called_once()
    mock_config.AioConfig.assert_called_once_with(
        connect_timeout=5,
        read_timeout=10,
        max_pool_connections=10,
        retries={"max_attempts": 3, "mode": "standard"},
        s3={"addressing_style": "path"},
    )
    mock_session.get_session.return_value.create_client.assert_called_once_with(
        "s3",
        endpoint_url=f"http://{os.environ['MINIO_HOST']}:{os.environ['MINIO_PORT']}",
        use_ssl=False,
        aws_access_key_id=os.environ["MINIO_ROOT_USER"],
        aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"],
        config=mock_config.AioConfig.return_value,
    )
    assert client == mock_session.get_session.return_value.create_client.return_value


@patch("di.di.inject.Binder")
@patch("di.di.sessionmaker_factory")
@patch("di.di.client_factory")
def test_configure_inject(mock_client_factory, mock_sessionmaker_factory, mock_binder):
    configure_inject(mock_binder)

    expected_calls = [
        call(async_sessionmaker[AsyncSession], mock_sessionmaker_factory),
        call(S3Client, mock_client_factory),
    ]

    mock_binder.bind_to_provider.assert_has_calls(expected_calls, any_order=True)
    assert mock_binder.bind_to_provider.call_count == 2


@patch("di.di.inject.configure")
@patch("di.di.configure_inject")
def test_setup_di(mock_configure_inject, mock_inject_configure):
    setup_di()
    mock_inject_configure.assert_called_once_with(mock_configure_inject, once=True)
