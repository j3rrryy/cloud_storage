import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import AsyncTestClient

from controller import v1 as controller_v1
from service import v1 as service_v1

from .mocks import create_auth_stub_v1, create_file_stub_v1, create_mail_producer


async def auth_service_v1_factory() -> AsyncGenerator[service_v1.AuthService, None]:
    yield service_v1.AuthService(create_auth_stub_v1())


async def file_service_v1_factory() -> AsyncGenerator[service_v1.FileService, None]:
    yield service_v1.FileService(create_file_stub_v1())


async def mail_service_v1_factory() -> AsyncGenerator[service_v1.MailService, None]:
    yield service_v1.MailService(create_mail_producer())


def create_app() -> Litestar:
    app = Litestar(
        path="/api",
        route_handlers=(controller_v1.auth_router, controller_v1.file_router),
        debug=bool(int(os.environ["DEBUG"])),
        dependencies={
            "auth_service_v1": Provide(auth_service_v1_factory),
            "file_service_v1": Provide(file_service_v1_factory),
            "mail_service_v1": Provide(mail_service_v1_factory),
        },
    )
    return app


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncTestClient[Litestar], None]:
    async with AsyncTestClient(app=create_app()) as client:
        yield client


@pytest.fixture()
def auth_service_v1() -> service_v1.AuthService:
    return service_v1.AuthService(create_auth_stub_v1())


@pytest.fixture()
def file_service_v1() -> service_v1.FileService:
    return service_v1.FileService(create_file_stub_v1())


@pytest.fixture
def mail_service_v1() -> service_v1.MailService:
    return service_v1.MailService(create_mail_producer())
