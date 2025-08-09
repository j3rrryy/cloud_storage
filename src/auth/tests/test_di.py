import os
from unittest.mock import AsyncMock, call, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from di import configure_inject, key_pair_factory, session_factory, setup_di
from utils import KeyPair


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


@patch("di.di.KeyPair")
def test_key_pair_factory(mock_key_pair):
    key_pair_factory()
    mock_key_pair.assert_called_once()


@patch("di.di.inject.Binder")
@patch("di.di.session_factory")
@patch("di.di.key_pair_factory")
def test_configure_inject(mock_key_pair_factory, mock_session_factory, mock_binder):
    configure_inject(mock_binder)

    expected_calls = [
        call(AsyncSession, mock_session_factory),
        call(KeyPair, mock_key_pair_factory),
    ]

    mock_binder.bind_to_provider.assert_has_calls(expected_calls, any_order=True)
    assert mock_binder.bind_to_provider.call_count == 2


@patch("di.di.inject.configure")
@patch("di.di.configure_inject")
def test_setup_di(mock_configure_inject, mock_inject_configure):
    setup_di()
    mock_inject_configure.assert_called_once_with(mock_configure_inject, once=True)
