from typing import Generator
from unittest.mock import MagicMock

import inject
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from controller import AuthController
from repository import TokenPair, User
from utils import KeyPair, get_hashed_password

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
def mock_sessionmaker() -> Generator[async_sessionmaker[AsyncSession], None, None]:
    mock_sessionmaker = MagicMock(spec=async_sessionmaker[AsyncSession])
    inject.clear_and_configure(
        lambda binder: binder.bind(async_sessionmaker[AsyncSession], mock_sessionmaker)
    )
    yield mock_sessionmaker
    inject.clear()


@pytest.fixture
def mock_key_pair() -> Generator[KeyPair, None, None]:
    mock_key_pair = KeyPair()
    inject.clear_and_configure(lambda binder: binder.bind(KeyPair, mock_key_pair))
    yield mock_key_pair
    inject.clear()


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
