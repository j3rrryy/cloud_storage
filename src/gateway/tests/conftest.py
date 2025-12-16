from typing import AsyncGenerator, Callable

import pytest
import pytest_asyncio
from aiokafka import AIOKafkaProducer
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import AsyncTestClient

from adapters import AuthGrpcAdapter, FileGrpcAdapter, MailKafkaAdapter
from controller import v1 as controller_v1
from facades import ApplicationFacade, AuthFacade, FileFacade
from proto import AuthStub, FileStub
from protocols import (
    ApplicationFacadeProtocol,
    AuthFacadeProtocol,
    AuthServiceProtocol,
    FileFacadeProtocol,
    FileServiceProtocol,
    MailServiceProtocol,
)
from settings import Settings

from .mocks import create_auth_stub_v1, create_file_stub_v1, create_mail_producer


@pytest.fixture
def auth_stub_v1() -> AuthStub:
    return create_auth_stub_v1()


@pytest.fixture
def file_stub_v1() -> FileStub:
    return create_file_stub_v1()


@pytest.fixture
def producer() -> AIOKafkaProducer:
    return create_mail_producer()


@pytest.fixture
def auth_grpc_adapter(auth_stub_v1) -> AuthServiceProtocol:
    return AuthGrpcAdapter(auth_stub_v1)


@pytest.fixture
def file_grpc_adapter(file_stub_v1) -> FileServiceProtocol:
    return FileGrpcAdapter(file_stub_v1)


@pytest.fixture
def mail_kafka_adapter(producer) -> MailServiceProtocol:
    return MailKafkaAdapter(producer)


@pytest.fixture
def auth_facade(auth_grpc_adapter, mail_kafka_adapter) -> AuthFacadeProtocol:
    return AuthFacade(auth_grpc_adapter, mail_kafka_adapter)


@pytest.fixture
def file_facade(file_grpc_adapter) -> FileFacadeProtocol:
    return FileFacade(file_grpc_adapter)


@pytest.fixture
def application_facade_factory(
    auth_facade, file_facade
) -> Callable[[], ApplicationFacadeProtocol]:
    def _application_facade_factory() -> ApplicationFacadeProtocol:
        return ApplicationFacade(auth_facade, file_facade)

    return _application_facade_factory


@pytest.fixture
def application_facade(application_facade_factory) -> ApplicationFacadeProtocol:
    return application_facade_factory()


@pytest.fixture
def app(application_facade_factory) -> Litestar:
    return Litestar(
        path="/api",
        route_handlers=(controller_v1.auth_router, controller_v1.file_router),
        debug=Settings.DEBUG,
        dependencies={
            "application_facade": Provide(
                application_facade_factory, use_cache=True, sync_to_thread=False
            )
        },
    )


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncTestClient[Litestar], None]:
    async with AsyncTestClient(app) as client:
        yield client
