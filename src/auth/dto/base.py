from dataclasses import asdict as dc_asdict
from dataclasses import dataclass, replace
from typing import Any, Type, TypeVar

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound="BaseDTO")
Request = TypeVar("Request", bound="BaseRequestDTO")
Response = TypeVar("Response", bound="BaseResponseDTO")


@dataclass(slots=True, frozen=True)
class BaseDTO:
    def dict(self) -> dict[str, Any]:
        return {k: v for k, v in dc_asdict(self).items() if v is not None}

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
        return cls(**{k: getattr(model, k) for k in model.__mapper__.c.keys()})
