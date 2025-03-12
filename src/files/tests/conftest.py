from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from types_aiobotocore_s3 import S3Client

from database import File
from service import FilesServicer

from .mocks import FILE_ID, NAME, PATH, SIZE, TIMESTAMP, USER_ID


@pytest.fixture
def mock_session() -> AsyncSession:
    session = AsyncMock(AsyncSession)
    session.add = MagicMock()
    session.delete = AsyncMock()
    session.refresh = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.execute = AsyncMock(return_value=MagicMock())
    session.execute.return_value.scalar_one_or_none = MagicMock()
    session.execute.return_value.scalars = MagicMock(return_value=MagicMock())
    session.execute.return_value.scalars.return_value.all = MagicMock()
    return session


@pytest.fixture
def mock_client() -> S3Client:
    client = AsyncMock(S3Client)
    client.head_bucket = AsyncMock()
    client.head_object = AsyncMock()
    client.delete_object = AsyncMock()
    client.delete_objects = AsyncMock()
    client.generate_presigned_url = AsyncMock()
    client.get_paginator = MagicMock(return_value=AsyncMock())
    return client


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
def files_servicer() -> FilesServicer:
    return FilesServicer()
