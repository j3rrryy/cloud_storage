from dataclasses import asdict, dataclass, replace
from typing import Type, TypeVar

from google.protobuf.message import Message
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound="BaseDTO")
Request = TypeVar("Request", bound="BaseRequestDTO")
Response = TypeVar("Response", bound="BaseResponseDTO")
Model = TypeVar("Model", bound=DeclarativeBase)
GrpcMessage = TypeVar("GrpcMessage", bound=Message)


@dataclass(slots=True, frozen=True)
class BaseDTO:
    def replace(self: T, **kwargs) -> T:
        return replace(self, **kwargs)


@dataclass(slots=True, frozen=True)
class BaseRequestDTO(BaseDTO):
    @classmethod
    def from_request(cls: Type[Request], request: Message) -> Request:
        return cls(*(getattr(request, f) for f in cls.__dataclass_fields__.keys()))

    def to_model(self, model: type[Model]) -> Model:
        return model(**asdict(self))


@dataclass(slots=True, frozen=True)
class BaseResponseDTO(BaseDTO):
    @classmethod
    def from_model(cls: Type[Response], model: DeclarativeBase) -> Response:
        return cls(*(getattr(model, f) for f in cls.__dataclass_fields__.keys()))

    def to_response(self, message: Type[GrpcMessage]) -> GrpcMessage:
        fields = {f.name: getattr(self, f.name) for f in message.DESCRIPTOR.fields}
        return message(**fields)
