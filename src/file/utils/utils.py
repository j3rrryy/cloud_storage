import os
from functools import wraps
from typing import Awaitable, Callable, TypeVar

import inject
import picologging as logging
from grpc import ServicerContext, StatusCode
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from types_aiobotocore_s3 import S3Client

T = TypeVar("T")

BUCKET_NAME = os.environ["MINIO_FILE_BUCKET"]

logger = logging.getLogger()


class ExceptionHandler:
    @staticmethod
    async def handle(
        context: ServicerContext, func: Callable[..., Awaitable[T]], *args, **kwargs
    ) -> T:
        try:
            return await func(*args, **kwargs)
        except Exception as exc:
            status_code, details = exc.args
            logger.error(
                f"Status code: {status_code.name} ({status_code.value[0]}), details: {details}"
            )
            await context.abort(status_code, details)  # type: ignore
            raise


def with_transaction(func):
    @wraps(func)
    @inject.autoparams()
    async def wrapper(*args, sessionmaker: async_sessionmaker[AsyncSession], **kwargs):
        async with sessionmaker() as session:
            try:
                return await func(*args, session, **kwargs)
            except Exception as exc:
                await session.rollback()
                if not isinstance(exc, (IntegrityError, FileNotFoundError)):
                    exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
                raise exc

    return wrapper


def with_storage(func):
    @wraps(func)
    @inject.autoparams()
    async def wrapper(*args, client: S3Client, **kwargs):
        async with client as _client:
            try:
                return await func(*args, _client, **kwargs)
            except Exception as exc:
                if not isinstance(exc, FileNotFoundError):
                    exc.args = (StatusCode.INTERNAL, f"Internal storage error, {exc}")
                raise exc

    return wrapper
