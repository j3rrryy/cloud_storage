from typing import Generator
from unittest.mock import AsyncMock, MagicMock

import inject
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from types_aiobotocore_s3 import S3Client

from controller import FileController
from repository import File

from .mocks import FILE_ID, NAME, PATH, SIZE, TIMESTAMP, USER_ID


@pytest.fixture
def mock_sessionmaker() -> Generator[async_sessionmaker[AsyncSession], None, None]:
    mock_sessionmaker = MagicMock(spec=async_sessionmaker[AsyncSession])
    inject.clear_and_configure(
        lambda binder: binder.bind(async_sessionmaker[AsyncSession], mock_sessionmaker)
    )
    yield mock_sessionmaker
    inject.clear()


@pytest.fixture
def mock_client() -> Generator[S3Client, None, None]:
    mock_client = AsyncMock(spec=S3Client)
    inject.clear_and_configure(lambda binder: binder.bind(S3Client, mock_client))
    yield mock_client
    inject.clear()


@pytest.fixture
def file() -> File:
    return File(
        file_id=FILE_ID,
        user_id=USER_ID,
        name=NAME,
        path=PATH,
        size=SIZE,
        uploaded=TIMESTAMP,
    )


@pytest.fixture(scope="session")
def file_controller() -> FileController:
    return FileController()
