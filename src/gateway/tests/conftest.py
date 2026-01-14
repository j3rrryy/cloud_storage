from typing import AsyncGenerator, Awaitable, Callable
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from aiokafka import AIOKafkaProducer
from litestar import Litestar
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.testing import AsyncTestClient

from adapters import AuthGrpcAdapter, FileGrpcAdapter, MailKafkaAdapter
from controller import HealthController
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
from utils import exception_handler

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
def application_facade(auth_facade, file_facade) -> ApplicationFacadeProtocol:
    return ApplicationFacade(auth_facade, file_facade)


@pytest.fixture
def is_ready() -> Callable[[], Awaitable[bool]]:
    return AsyncMock(spec=Callable[[], Awaitable[bool]], return_value=True)


@pytest.fixture
def app(is_ready, application_facade) -> Litestar:
    return Litestar(
        path="/api",
        route_handlers=(
            HealthController,
            controller_v1.auth_router,
            controller_v1.file_router,
        ),
        debug=Settings.DEBUG,
        exception_handlers={HTTPException: exception_handler},
        dependencies={
            "is_ready": Provide(lambda: is_ready, use_cache=True, sync_to_thread=False),
            "application_facade": Provide(
                lambda: application_facade, use_cache=True, sync_to_thread=False
            ),
        },
    )


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncTestClient[Litestar], None]:
    async with AsyncTestClient(app) as client:
        yield client
