from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from controller import AuthController
from repository import TokenPair, User
from utils import get_hashed_password

from .mocks import (
    ACCESS_TOKEN,
    BROWSER,
    EMAIL,
    PASSWORD,
    REFRESH_TOKEN,
    SESSION_ID,
    TIMESTAMP,
    USER_ID,
    USER_IP,
    USERNAME,
)


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


@pytest.fixture(scope="session")
def user() -> User:
    return User(
        user_id=USER_ID,
        username=USERNAME,
        email=EMAIL,
        password=get_hashed_password(PASSWORD),
        verified=True,
    )


@pytest.fixture(scope="session")
def token_pair() -> TokenPair:
    return TokenPair(
        session_id=SESSION_ID,
        user_id=USER_ID,
        access_token=ACCESS_TOKEN,
        refresh_token=REFRESH_TOKEN,
        user_ip=USER_IP,
        browser=BROWSER,
        last_accessed=TIMESTAMP,
    )


@pytest.fixture(scope="session")
def auth_controller() -> AuthController:
    return AuthController()
