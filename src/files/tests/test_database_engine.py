from unittest.mock import MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from config import load_config
from database.engine import _get_sessionmaker


@patch("database.engine.async_sessionmaker")
@patch("database.engine.create_async_engine")
@patch("database.engine.URL")
def test_get_client(mock_url, mock_create_async_engine, mock_async_sessionmaker):
    config = load_config()
    mock_created_url = MagicMock()
    mock_url.create = mock_created_url
    _get_sessionmaker()

    mock_created_url.assert_called_once_with(
        config.postgres.driver,
        config.postgres.user,
        config.postgres.password,
        config.postgres.host,
        config.postgres.port,
        config.postgres.database,
    )
    args, kwargs = mock_create_async_engine.call_args
    assert len(args) == 1
    assert kwargs == {"pool_pre_ping": True}
    args, kwargs = mock_async_sessionmaker.call_args
    assert len(args) == 1
    assert kwargs == {"class_": AsyncSession}
