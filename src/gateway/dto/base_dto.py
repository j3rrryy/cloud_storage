from dataclasses import asdict, dataclass
from typing import Type, TypeVar

import msgspec
from google.protobuf.message import Message
from google.protobuf.timestamp_pb2 import Timestamp
from msgspec import Struct

T = TypeVar("T", bound="BaseDTO")
GrpcMessage = TypeVar("GrpcMessage", bound=Message)
MsgspecStruct = TypeVar("MsgspecStruct", bound=Struct)


@dataclass(slots=True, frozen=True)
class BaseDTO: ...


@dataclass(slots=True, frozen=True)
class FromSchemaMixin(BaseDTO):
    @classmethod
    def from_schema(cls: Type[T], schema: Struct) -> T:
        return cls(*(getattr(schema, f) for f in cls.__dataclass_fields__.keys()))


@dataclass(slots=True, frozen=True)
class ToRequestMixin(BaseDTO):
    def to_request(self, message: type[GrpcMessage]) -> GrpcMessage:
        fields = {f.name: getattr(self, f.name) for f in message.DESCRIPTOR.fields}
        return message(**fields)


@dataclass(slots=True, frozen=True)
class FromResponseMixin(BaseDTO):
    @classmethod
    def from_response(cls: Type[T], message: Message) -> T:
        fields = []
        for f in cls.__dataclass_fields__.keys():
            field = getattr(message, f)
            if isinstance(field, Timestamp):
                field = field.ToDatetime()
            fields.append(field)
        return cls(*fields)


@dataclass(slots=True, frozen=True)
class ToSchemaMixin(BaseDTO):
    def to_schema(self, schema: type[MsgspecStruct]) -> MsgspecStruct:
        return schema(*(getattr(self, f) for f in schema.__struct_fields__))


@dataclass(slots=True, frozen=True)
class ToMsgpackMixin(BaseDTO):
    def to_msgpack(self) -> bytes:
        return msgspec.msgpack.encode(asdict(self))
