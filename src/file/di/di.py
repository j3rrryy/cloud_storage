import os

import inject
from aiobotocore import config, session
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from types_aiobotocore_s3 import S3Client


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


def client_factory() -> session.ClientCreatorContext:
    aiosession = session.get_session()
    aioconfig = config.AioConfig(
        connect_timeout=5,
        read_timeout=10,
        max_pool_connections=10,
        retries={"max_attempts": 3, "mode": "standard"},
        s3={"addressing_style": "path"},
    )
    client = aiosession.create_client(
        "s3",
        endpoint_url=f"http://{os.environ['MINIO_HOST']}:{os.environ['MINIO_PORT']}",
        use_ssl=False,
        aws_access_key_id=os.environ["MINIO_ROOT_USER"],
        aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"],
        config=aioconfig,
    )
    return client


def configure_inject(binder: inject.Binder) -> None:
    binder.bind_to_provider(async_sessionmaker[AsyncSession], sessionmaker_factory)
    binder.bind_to_provider(S3Client, client_factory)


def setup_di() -> None:
    inject.configure(configure_inject, once=True)
