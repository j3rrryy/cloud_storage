import pytest

from controller import AuthController
from repository import TokenPair, User
from security import get_password_hash

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


@pytest.fixture(scope="session")
def user() -> User:
    return User(
        user_id=USER_ID,
        username=USERNAME,
        email=EMAIL,
        password=get_password_hash(PASSWORD),
        email_confirmed=True,
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
        created_at=TIMESTAMP,
    )


@pytest.fixture(scope="session")
def auth_controller() -> AuthController:
    return AuthController()
