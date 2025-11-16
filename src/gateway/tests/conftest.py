import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import AsyncTestClient

from adapters import AuthGrpcAdapter, FileGrpcAdapter, MailKafkaAdapter
from controller import v1 as controller_v1
from facades import ApplicationFacade

from .mocks import create_auth_stub_v1, create_file_stub_v1, create_mail_producer


async def application_facade_factory() -> AsyncGenerator[ApplicationFacade, None]:
    auth_adapter = AuthGrpcAdapter(create_auth_stub_v1())
    file_adapter = FileGrpcAdapter(create_file_stub_v1())
    mail_adapter = MailKafkaAdapter(create_mail_producer())
    facade = ApplicationFacade(auth_adapter, file_adapter, mail_adapter)
    yield facade


async def auth_adapter_factory() -> AsyncGenerator[AuthGrpcAdapter, None]:
    adapter = AuthGrpcAdapter(create_auth_stub_v1())
    yield adapter


async def file_adapter_factory() -> AsyncGenerator[FileGrpcAdapter, None]:
    adapter = FileGrpcAdapter(create_file_stub_v1())
    yield adapter


async def mail_adapter_factory() -> AsyncGenerator[MailKafkaAdapter, None]:
    adapter = MailKafkaAdapter(create_mail_producer())
    yield adapter


def create_app() -> Litestar:
    app = Litestar(
        path="/api",
        route_handlers=(controller_v1.auth_router, controller_v1.file_router),
        debug=bool(int(os.environ["DEBUG"])),
        dependencies={
            "application_facade": Provide(application_facade_factory),
            "auth_service": Provide(auth_adapter_factory),
            "file_service": Provide(file_adapter_factory),
            "mail_service": Provide(mail_adapter_factory),
        },
    )
    return app


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncTestClient[Litestar], None]:
    async with AsyncTestClient(app=create_app()) as client:
        yield client


@pytest.fixture()
def application_facade() -> ApplicationFacade:
    auth_adapter = AuthGrpcAdapter(create_auth_stub_v1())
    file_adapter = FileGrpcAdapter(create_file_stub_v1())
    mail_adapter = MailKafkaAdapter(create_mail_producer())
    return ApplicationFacade(auth_adapter, file_adapter, mail_adapter)


@pytest.fixture()
def auth_service() -> AuthGrpcAdapter:
    return AuthGrpcAdapter(create_auth_stub_v1())


@pytest.fixture()
def file_service() -> FileGrpcAdapter:
    return FileGrpcAdapter(create_file_stub_v1())


@pytest.fixture()
def mail_service() -> MailKafkaAdapter:
    return MailKafkaAdapter(create_mail_producer())
