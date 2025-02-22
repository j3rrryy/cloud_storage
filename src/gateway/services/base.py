import pickle
from functools import wraps
from typing import Type, TypeVar

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message
from grpc import StatusCode, aio
from litestar.exceptions import (
    HTTPException,
    InternalServerException,
    NotAuthorizedException,
    NotFoundException,
    PermissionDeniedException,
)

from dto.base import BaseDTO

T = TypeVar("T", bound=BaseDTO)


class RPCBase:
    __slots__ = "_stub"

    _instance = None
    _converted_exceptions = {
        StatusCode.ALREADY_EXISTS: HTTPException(status_code=409),
        StatusCode.UNAUTHENTICATED: NotAuthorizedException,
        StatusCode.NOT_FOUND: NotFoundException,
        StatusCode.PERMISSION_DENIED: PermissionDeniedException,
        StatusCode.INTERNAL: InternalServerException,
        StatusCode.UNAVAILABLE: InternalServerException,
        StatusCode.UNKNOWN: InternalServerException,
    }

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, stub):
        self._stub = stub

    @classmethod
    def handle_exception(cls, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except aio.AioRpcError as exc:
                converted = cls._converted_exceptions[exc.code()]
                converted.detail = exc.details()
                raise converted

        return wrapper

    @staticmethod
    def convert_to_dto(data: Message, dto: Type[T]) -> T:
        return dto(**MessageToDict(data, preserving_proto_field_name=True))


class KafkaBase:
    __slots__ = "_producer"

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, producer):
        self._producer = producer

    @staticmethod
    def serialize_dict(d: dict[str, str]) -> bytes:
        return pickle.dumps(d)
