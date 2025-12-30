from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import inject
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from settings import Settings
from utils import KeyPair


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
                Settings.POSTGRES_DRIVER,
                Settings.POSTGRES_USER,
                Settings.POSTGRES_PASSWORD,
                Settings.POSTGRES_HOST,
                Settings.POSTGRES_PORT,
                Settings.POSTGRES_DB,
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


def key_pair_factory() -> KeyPair:
    return KeyPair()


def configure_inject(binder: inject.Binder) -> None:
    binder.bind_to_provider(AsyncSession, SessionManager.session_factory)
    binder.bind_to_provider(KeyPair, key_pair_factory)


async def setup_di() -> None:
    await SessionManager.setup()
    inject.configure(configure_inject, once=True)
