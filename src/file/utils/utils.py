from datetime import datetime, timezone
from functools import wraps
from typing import Awaitable, Callable

import grpc
import picologging as logging
from botocore.exceptions import ClientError

from exceptions import (
    BaseAppException,
    DatabaseException,
    FileNotFoundException,
    StorageException,
)


class ExceptionInterceptor(grpc.aio.ServerInterceptor):  # pragma: no cover
    logger = logging.getLogger()

    async def intercept_service(
        self,
        continuation: Callable[
            [grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]
        ],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        handler = await continuation(handler_call_details)

        async def wrapper(request, context):
            try:
                return await handler.unary_unary(request, context)  # type: ignore
            except BaseAppException as exc:
                status_code = getattr(exc, "status_code", grpc.StatusCode.UNKNOWN)
                details = getattr(exc, "details", str(exc))
                self.logger.info(f"Status code: {status_code.name}, details: {details}")
                await context.abort(status_code, details)
                return

        return handler._replace(unary_unary=wrapper)  # type: ignore


def database_exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as exc:
            if isinstance(exc, BaseAppException):
                raise exc
            raise DatabaseException(exc)

    return wrapper


def storage_exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ClientError as exc:
            if exc.response["Error"]["Code"] in {"NoSuchKey", "404"}:  # type: ignore
                raise FileNotFoundException
            raise StorageException(exc)
        except Exception as exc:
            raise StorageException(exc)

    return wrapper


def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
