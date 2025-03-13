from functools import wraps
from typing import Awaitable, Callable, TypeVar

from grpc import ServicerContext, StatusCode
from picologging import Logger
from sqlalchemy.exc import IntegrityError

T = TypeVar("T")


class ExceptionHandler:
    __slots__ = "_logger"

    def __init__(self, logger: Logger):
        self._logger = logger

    async def __call__(
        self,
        context: ServicerContext,
        func: Callable[..., Awaitable[T]],
        *args,
        **kwargs,
    ) -> T:
        try:
            res = await func(*args, **kwargs)
            return res
        except Exception as exc:
            status_code, details = exc.args
            self._logger.error(
                f"Status code: {status_code.name} ({status_code.value[0]}), details: {details}"
            )
            await context.abort(status_code, details)
            raise


def repository_exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            res = await func(*args, **kwargs)
            return res
        except IntegrityError as exc:
            await kwargs["session"].rollback()
            raise exc
        except FileNotFoundError as exc:
            raise exc
        except Exception as exc:
            await kwargs["session"].rollback()
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    return wrapper


def storage_exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            res = await func(*args, **kwargs)
            return res
        except FileNotFoundError as exc:
            raise exc
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, f"Internal storage error, {exc}")
            raise exc

    return wrapper
