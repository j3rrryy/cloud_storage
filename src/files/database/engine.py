from functools import wraps

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import load_config

__all__ = ["get_session"]


def _get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    config = load_config()
    postgres_url = URL.create(
        config.postgres.driver,
        config.postgres.user,
        config.postgres.password,
        config.postgres.host,
        config.postgres.port,
        config.postgres.database,
    )

    async_engine = create_async_engine(postgres_url, pool_pre_ping=True)
    sessionmaker = async_sessionmaker(async_engine, class_=AsyncSession)
    return sessionmaker


_sessionmaker = _get_sessionmaker()


def get_session(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with _sessionmaker() as session:
            res = await func(*args, **kwargs, session=session)
            return res

    return wrapper
