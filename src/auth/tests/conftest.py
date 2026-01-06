import pytest
from cashews import Cache
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from controller import AuthController
from proto import AuthServicer
from protocols import AuthRepositoryProtocol, AuthServiceProtocol
from repository import AuthRepository, TokenPair, User
from service import AuthService

from .mocks import (
    create_auth_repository,
    create_cache,
    create_session,
    create_sessionmaker,
    create_token_pair,
    create_user,
)


@pytest.fixture
def session() -> AsyncSession:
    return create_session()


@pytest.fixture
def sessionmaker(session) -> async_sessionmaker[AsyncSession]:
    return create_sessionmaker(session)


@pytest.fixture
def cache() -> Cache:
    return create_cache()


@pytest.fixture
def auth_repository(sessionmaker) -> AuthRepositoryProtocol:
    return AuthRepository(sessionmaker)


@pytest.fixture
def mocked_auth_repository() -> AuthRepositoryProtocol:
    return create_auth_repository()


@pytest.fixture
def auth_service(mocked_auth_repository, cache) -> AuthServiceProtocol:
    return AuthService(mocked_auth_repository, cache)


@pytest.fixture
def auth_controller(auth_service) -> AuthServicer:
    return AuthController(auth_service)


@pytest.fixture
def user() -> User:
    return create_user()


@pytest.fixture
def token_pair() -> TokenPair:
    return create_token_pair()
