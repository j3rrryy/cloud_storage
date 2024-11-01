from functools import wraps

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import load_config

__all__ = ["get_session"]


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    config = load_config()
    postgres_url = URL.create(
        drivername=config.postgres.driver,
        username=config.postgres.user,
        password=config.postgres.password,
        host=config.postgres.host,
        port=int(config.postgres.port),
        database=config.postgres.database,
    )

    async_engine = create_async_engine(url=postgres_url, pool_pre_ping=True)
    sessionmaker = async_sessionmaker(bind=async_engine, class_=AsyncSession)
    return sessionmaker


def get_session(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with get_sessionmaker()() as session:
            result = await func(*args, **kwargs, session=session)
            return result

    return wrapper
