from dataclasses import asdict
from functools import wraps
from typing import Type, TypeVar

import msgspec
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message
from grpc import StatusCode, aio
from litestar.exceptions import (
    HTTPException,
    InternalServerException,
    NotAuthorizedException,
    NotFoundException,
    ServiceUnavailableException,
)

from dto import BaseDTO

T = TypeVar("T", bound=BaseDTO)


class RPCBaseService:
    __slots__ = "_stub"

    _instance = None
    _converted_exceptions = {
        StatusCode.ALREADY_EXISTS: HTTPException(status_code=409),
        StatusCode.UNAUTHENTICATED: NotAuthorizedException,
        StatusCode.NOT_FOUND: NotFoundException,
        StatusCode.RESOURCE_EXHAUSTED: ServiceUnavailableException,
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
                    exc.code(), InternalServerException
                )
                converted.detail = exc.details()
                raise converted

        return wrapper

    @staticmethod
    def convert_to_dto(data: Message, dto: Type[T]) -> T:
        return dto(**MessageToDict(data, preserving_proto_field_name=True))


class KafkaBaseService:
    __slots__ = "_producer"

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, producer):
        self._producer = producer

    @staticmethod
    def serialize_dto(dto: BaseDTO) -> bytes:
        return msgspec.msgpack.encode(asdict(dto))
