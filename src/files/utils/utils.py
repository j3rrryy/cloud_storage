from typing import Awaitable, Callable, TypeVar

from grpc import ServicerContext
from picologging import Logger

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
