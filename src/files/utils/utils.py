from typing import Any

from grpc import ServicerContext
from picologging import Logger


class ExceptionHandler:
    __slots__ = "_logger"

    def __init__(self, logger: Logger):
        self._logger = logger

    async def __call__(self, context: ServicerContext, func, *args, **kwargs) -> Any:
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as exc:
            status_code, details = exc.args
            self._logger.error(
                f"Status code: {status_code.name} ({status_code.value[0]}), details: {details}, {exc}"
            )
            await context.abort(status_code, details)
