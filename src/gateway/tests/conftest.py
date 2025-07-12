import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import AsyncTestClient

from controller.v1 import auth_router_v1, file_router_v1
from service.v1 import AuthService, FileService, MailService

from .mocks import create_auth_stub, create_file_stub, create_mail_producer


async def auth_service_factory() -> AsyncGenerator[AuthService, None]:
    yield AuthService(create_auth_stub())


async def file_service_factory() -> AsyncGenerator[FileService, None]:
    yield FileService(create_file_stub())


async def mail_service_factory() -> AsyncGenerator[MailService, None]:
    yield MailService(create_mail_producer())


def create_app() -> Litestar:
    app = Litestar(
        path="/api",
        route_handlers=(auth_router_v1, file_router_v1),
        debug=bool(int(os.environ["DEBUG"])),
        dependencies={
            "auth_service": Provide(auth_service_factory),
            "file_service": Provide(file_service_factory),
            "mail_service": Provide(mail_service_factory),
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
