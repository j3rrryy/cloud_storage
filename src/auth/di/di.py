import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import inject
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from utils import KeyPair


@asynccontextmanager
async def session_factory() -> AsyncGenerator[AsyncSession, None]:
    postgres_url = URL.create(
        os.environ["POSTGRES_DRIVER"],
        os.environ["POSTGRES_USER"],
        os.environ["POSTGRES_PASSWORD"],
        os.environ["POSTGRES_HOST"],
        int(os.environ["POSTGRES_PORT"]),
        os.environ["POSTGRES_DB"],
    )
    async_engine = create_async_engine(
        postgres_url,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
    )
    sessionmaker = async_sessionmaker(async_engine, class_=AsyncSession)
    async with sessionmaker() as session:
        yield session


def key_pair_factory() -> KeyPair:
    return KeyPair()


def configure_inject(binder: inject.Binder) -> None:
    binder.bind_to_provider(AsyncSession, session_factory)
    binder.bind_to_provider(KeyPair, key_pair_factory)


def setup_di() -> None:
    inject.configure(configure_inject, once=True)
