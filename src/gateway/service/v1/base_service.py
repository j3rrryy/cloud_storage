from functools import wraps

from grpc import StatusCode, aio
from litestar.exceptions import (
    HTTPException,
    InternalServerException,
    NotAuthorizedException,
    NotFoundException,
    ServiceUnavailableException,
)


class RPCBaseService:
    __slots__ = "_stub"

    _instance = None
    _converted_exceptions = {
        StatusCode.ALREADY_EXISTS: lambda detail: HTTPException(
            detail=detail, status_code=409
        ),
        StatusCode.UNAUTHENTICATED: lambda detail: NotAuthorizedException(
            detail=detail
        ),
        StatusCode.NOT_FOUND: lambda detail: NotFoundException(detail=detail),
        StatusCode.RESOURCE_EXHAUSTED: lambda detail: ServiceUnavailableException(
            detail=detail
        ),
        StatusCode.UNAVAILABLE: lambda detail: ServiceUnavailableException(
            detail=detail
        ),
    }

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, stub):
        self._stub = stub

    @classmethod
    def exception_handler(cls, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
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


class KafkaBaseService:
    __slots__ = "_producer"

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, producer):
        self._producer = producer
