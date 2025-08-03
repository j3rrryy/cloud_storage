import os

import inject
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from utils import KeyPair


def sessionmaker_factory() -> async_sessionmaker[AsyncSession]:
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
        pool_size=10,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
    )
    sessionmaker = async_sessionmaker(async_engine, class_=AsyncSession)
    return sessionmaker


def key_pair_factory() -> KeyPair:
    return KeyPair()


def configure_inject(binder: inject.Binder) -> None:
    binder.bind_to_provider(async_sessionmaker[AsyncSession], sessionmaker_factory)
    binder.bind_to_provider(KeyPair, key_pair_factory)


def setup_di() -> None:
    inject.configure(configure_inject, once=True)
