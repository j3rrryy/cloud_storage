from typing import Generator
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from types_aiobotocore_s3 import S3Client

from controller import FileController
from repository import File

from .mocks import FILE_ID, NAME, SIZE, TIMESTAMP, USER_ID


@pytest.fixture
def file() -> File:
    return File(
        file_id=FILE_ID, user_id=USER_ID, name=NAME, size=SIZE, uploaded_at=TIMESTAMP
    )


@pytest.fixture(scope="session")
def file_controller() -> FileController:
    return FileController()
