from collections.abc import Callable
from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import AsyncTestClient

from config import load_config
from routes.v1.auth import auth_router as auth_v1
from routes.v1.files import files_router as files_v1
from services import Auth, Files, Mail

from .mocks import create_auth_stub, create_files_stub, create_mail_producer


def connect_auth_service(verified: bool) -> Callable[[], AsyncGenerator[Auth, None]]:
    async def wrapper() -> AsyncGenerator[Auth, Any]:
        yield Auth(create_auth_stub(verified))

    return wrapper


async def connect_files_service() -> AsyncGenerator[Files, None]:
    yield Files(create_files_stub())


async def connect_mail_service() -> AsyncGenerator[Mail, None]:
    yield Mail(create_mail_producer())


def create_app(verified: bool) -> Litestar:
    app = Litestar(
        path="/api",
        route_handlers=(auth_v1, files_v1),
        debug=load_config().app.debug,
        dependencies={
            "auth_service": Provide(connect_auth_service(verified)),
            "files_service": Provide(connect_files_service),
            "mail_service": Provide(connect_mail_service),
        },
    )
    return app


@pytest_asyncio.fixture(scope="session")
async def verified_client() -> AsyncGenerator[AsyncTestClient[Litestar], None]:
    async with AsyncTestClient(app=create_app(True)) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def unverified_client() -> AsyncGenerator[AsyncTestClient[Litestar], None]:
    async with AsyncTestClient(app=create_app(False)) as client:
        yield client


@pytest.fixture(scope="session")
def auth_service() -> Auth:
    return Auth(create_auth_stub(True))


@pytest.fixture(scope="session")
def files_service() -> Files:
    return Files(create_files_stub())


@pytest.fixture
def mail_service() -> Mail:
    return Mail(create_mail_producer())
