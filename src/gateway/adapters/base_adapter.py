from abc import ABC
from functools import wraps
from typing import Awaitable, Callable, TypeVar

from aiokafka import AIOKafkaProducer
from grpc import StatusCode, aio
from litestar.exceptions import (
    HTTPException,
    InternalServerException,
    NotAuthorizedException,
    NotFoundException,
    ServiceUnavailableException,
    ValidationException,
)

T = TypeVar("T")


class BaseAdapter(ABC):
    _converted_exceptions = {
        StatusCode.ALREADY_EXISTS: lambda detail: HTTPException(
            detail=detail, status_code=409
        ),
        StatusCode.UNAUTHENTICATED: lambda detail: NotAuthorizedException(
            detail=detail
        ),
        StatusCode.NOT_FOUND: lambda detail: NotFoundException(detail=detail),
        StatusCode.INVALID_ARGUMENT: lambda detail: ValidationException(detail=detail),
        StatusCode.RESOURCE_EXHAUSTED: lambda detail: ServiceUnavailableException(
            detail=detail
        ),
        StatusCode.UNAVAILABLE: lambda detail: ServiceUnavailableException(
            detail=detail
        ),
    }

    @classmethod
    def exception_handler(
        cls, func: Callable[..., Awaitable[T]]
    ) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                result = await func(*args, **kwargs)
                return result
            except aio.AioRpcError as exc:
                converted = cls._converted_exceptions.get(
                    exc.code(), lambda detail: InternalServerException(detail=detail)
                )
                converted.detail = exc.details()
                raise converted(exc.details())

        return wrapper


class BaseRPCAdapter(BaseAdapter):
    __slots__ = "_stub"

    def __init__(self, stub):
        self._stub = stub


class BaseKafkaAdapter(BaseAdapter):
    __slots__ = "_producer"

    def __init__(self, producer: AIOKafkaProducer):
        self._producer = producer
