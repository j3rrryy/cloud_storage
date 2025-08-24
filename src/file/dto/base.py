from dataclasses import dataclass, replace
from typing import Type, TypeVar

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound="BaseDTO")
Request = TypeVar("Request", bound="BaseRequestDTO")
Response = TypeVar("Response", bound="BaseResponseDTO")


@dataclass(slots=True, frozen=True)
class BaseDTO:
    def replace(self: T, **kwargs) -> T:
        return replace(self, **kwargs)


@dataclass(slots=True, frozen=True)
class BaseRequestDTO(BaseDTO):
    @classmethod
    def from_request(cls: Type[Request], request: Message) -> Request:
        return cls(**MessageToDict(request, preserving_proto_field_name=True))


@dataclass(slots=True, frozen=True)
class BaseResponseDTO(BaseDTO):
    @classmethod
    def from_model(cls: Type[Response], model: DeclarativeBase) -> Response:
        fields = [f.name for f in cls.__dataclass_fields__.values()]
        return cls(*(getattr(model, f) for f in fields))
