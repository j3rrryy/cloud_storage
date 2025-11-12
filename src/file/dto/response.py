import datetime
from dataclasses import dataclass
from typing import Type, cast

from proto import file_pb2 as pb2

from .base import BaseResponseDTO, GrpcMessage


@dataclass(slots=True, frozen=True)
class UploadPartResponseDTO(BaseResponseDTO):
    part_number: int
    url: str


@dataclass(slots=True, frozen=True)
class InitiateUploadResponseDTO(BaseResponseDTO):
    file_id: str
    upload_id: str
    part_size: int
    parts: list[UploadPartResponseDTO]

    def to_response(self, message: Type[GrpcMessage]) -> pb2.InitiateUploadResponse:
        message_ = cast(Type[pb2.InitiateUploadResponse], message)
        return message_(
            upload_id=self.upload_id,
            part_size=self.part_size,
            parts=[part.to_response(pb2.UploadPart) for part in self.parts],
        )


@dataclass(slots=True, frozen=True)
class FileInfoResponseDTO(BaseResponseDTO):
    file_id: str
    user_id: str
    name: str
    size: int
    uploaded_at: datetime.datetime
