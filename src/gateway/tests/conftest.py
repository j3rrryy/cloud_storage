from typing import AsyncGenerator

import pytest
import pytest_asyncio
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import AsyncTestClient

from config import load_config
from routes.v1.auth import auth_router as auth_v1
from routes.v1.file import file_router as file_v1
from services import Auth, File, Mail

from .mocks import create_auth_stub, create_file_stub, create_mail_producer


async def connect_auth_service() -> AsyncGenerator[Auth, None]:
    yield Auth(create_auth_stub())


async def connect_file_service() -> AsyncGenerator[File, None]:
    yield File(create_file_stub())


async def connect_mail_service() -> AsyncGenerator[Mail, None]:
    yield Mail(create_mail_producer())


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
def auth_service() -> Auth:
    return Auth(create_auth_stub())


@pytest.fixture(scope="session")
def file_service() -> File:
    return File(create_file_stub())


@pytest.fixture
def mail_service() -> Mail:
    return Mail(create_mail_producer())
