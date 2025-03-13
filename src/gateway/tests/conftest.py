from typing import AsyncGenerator

import pytest
import pytest_asyncio
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import AsyncTestClient

from config import load_config
from controller.v1.auth import auth_router as auth_v1
from controller.v1.file import file_router as file_v1
from service import AuthService, FileService, MailService

from .mocks import create_auth_stub, create_file_stub, create_mail_producer


async def connect_auth_service() -> AsyncGenerator[AuthService, None]:
    yield AuthService(create_auth_stub())


async def connect_file_service() -> AsyncGenerator[FileService, None]:
    yield FileService(create_file_stub())


async def connect_mail_service() -> AsyncGenerator[MailService, None]:
    yield MailService(create_mail_producer())


def create_app() -> Litestar:
    app = Litestar(
        path="/api",
        route_handlers=(auth_v1, file_v1),
        debug=load_config().app.debug,
        dependencies={
            "auth_service": Provide(connect_auth_service),
            "file_service": Provide(connect_file_service),
            "mail_service": Provide(connect_mail_service),
        },
    )
    return app


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncTestClient[Litestar], None]:
    async with AsyncTestClient(app=create_app()) as client:
        yield client


@pytest.fixture(scope="session")
def auth_service() -> AuthService:
    return AuthService(create_auth_stub())


@pytest.fixture(scope="session")
def file_service() -> FileService:
    return FileService(create_file_stub())


@pytest.fixture
def mail_service() -> MailService:
    return MailService(create_mail_producer())
