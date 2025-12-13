from typing import AsyncGenerator

import pytest
import pytest_asyncio
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import AsyncTestClient

from adapters import AuthGrpcAdapter, FileGrpcAdapter, MailKafkaAdapter
from controller import v1 as controller_v1
from facades import ApplicationFacade, AuthFacade, FileFacade
from protocols import ApplicationFacadeProtocol
from settings import Settings

from .mocks import create_auth_stub_v1, create_file_stub_v1, create_mail_producer


def application_facade_factory() -> ApplicationFacadeProtocol:
    auth_adapter = AuthGrpcAdapter(create_auth_stub_v1())
    file_adapter = FileGrpcAdapter(create_file_stub_v1())
    mail_adapter = MailKafkaAdapter(create_mail_producer())
    auth_facade = AuthFacade(auth_adapter, mail_adapter)
    file_facade = FileFacade(file_adapter)
    return ApplicationFacade(auth_facade, file_facade)


def create_app() -> Litestar:
    app = Litestar(
        path="/api",
        route_handlers=(controller_v1.auth_router, controller_v1.file_router),
        debug=Settings.DEBUG,
        dependencies={"application_facade": Provide(application_facade_factory)},
    )
    return app


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncTestClient[Litestar], None]:
    async with AsyncTestClient(app=create_app()) as client:
        yield client


@pytest.fixture()
def application_facade() -> ApplicationFacadeProtocol:
    return application_facade_factory()
