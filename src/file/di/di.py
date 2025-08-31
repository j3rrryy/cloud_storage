import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import aioboto3
import inject
from aiobotocore.config import AioConfig
from aiobotocore.session import ClientCreatorContext
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from types_aiobotocore_s3 import S3Client


class SessionManager:
    sessionmaker: Optional[async_sessionmaker[AsyncSession]] = None
    _engine: Optional[AsyncEngine] = None
    _started = False

    @classmethod
    async def setup(cls) -> None:
        if cls._started:
            return
        try:
            postgres_url = URL.create(
                os.environ["POSTGRES_DRIVER"],
                os.environ["POSTGRES_USER"],
                os.environ["POSTGRES_PASSWORD"],
                os.environ["POSTGRES_HOST"],
                int(os.environ["POSTGRES_PORT"]),
                os.environ["POSTGRES_DB"],
            )
            cls._engine = create_async_engine(
                postgres_url,
                pool_pre_ping=True,
                pool_size=20,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=1800,
            )
            cls.sessionmaker = async_sessionmaker(
                cls._engine, class_=AsyncSession, expire_on_commit=False
            )
            cls._started = True
        except Exception:
            await cls.close()
            raise

    @classmethod
    async def close(cls) -> None:
        if cls._engine is not None:
            try:
                await cls._engine.dispose()
            finally:
                cls._engine = None
                cls.sessionmaker = None
        cls._started = False

    @classmethod
    @asynccontextmanager
    async def session_factory(cls) -> AsyncGenerator[AsyncSession, None]:
        if not cls.sessionmaker or not cls._started:
            raise RuntimeError(
                "Sessionmaker not initialized; SessionManager.setup() was not called"
            )
        async with cls.sessionmaker() as session:
            yield session


class ClientManager:
    client: Optional[S3Client] = None
    _context: Optional[ClientCreatorContext] = None
    _started = False

    @classmethod
    async def setup(cls) -> None:
        if cls._started:
            return
        try:
            session = aioboto3.Session()
            config = AioConfig(
                connect_timeout=5,
                read_timeout=10,
                max_pool_connections=30,
                retries={"max_attempts": 3, "mode": "standard"},
                s3={"addressing_style": "path"},
            )
            cls._context = session.client(
                "s3",
                use_ssl=False,
                verify=False,
                endpoint_url=f"http://{os.environ['MINIO_HOST']}:{os.environ['MINIO_PORT']}",
                aws_access_key_id=os.environ["MINIO_ROOT_USER"],
                aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"],
                config=config,
            )
            cls.client = await cls._context.__aenter__()
            cls._started = True
        except Exception:
            await cls.close()
            raise

    @classmethod
    async def close(cls) -> None:
        if cls._context is not None:
            try:
                await cls._context.__aexit__(None, None, None)
            finally:
                cls._context = None
                cls.client = None
        cls._started = False

    @classmethod
    def client_factory(cls) -> S3Client:
        if not cls.client or not cls._started:
            raise RuntimeError(
                "S3Client not initialized; ClientManager.setup() was not called"
            )
        return cls.client


def configure_inject(binder: inject.Binder) -> None:
    binder.bind_to_provider(AsyncSession, SessionManager.session_factory)
    binder.bind_to_provider(S3Client, ClientManager.client_factory)


async def setup_di() -> None:
    await SessionManager.setup()
    await ClientManager.setup()
    inject.configure(configure_inject, once=True)
