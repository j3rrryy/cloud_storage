import datetime
from dataclasses import dataclass
from typing import Type

from proto import file_pb2 as pb2
from schemas import file_schemas

from .base_dto import FromResponseMixin, ToRequestMixin, ToSchemaMixin


@dataclass(slots=True, frozen=True)
class InitiateUploadDTO(ToRequestMixin):
    user_id: str
    name: str
    size: int


@dataclass(slots=True, frozen=True)
class UploadPartDTO(FromResponseMixin, ToSchemaMixin):
    part_number: int
    url: str


@dataclass(slots=True, frozen=True)
class InitiatedUploadDTO(FromResponseMixin, ToSchemaMixin):
    upload_id: str
    part_size: int
    parts: list[UploadPartDTO]

    @classmethod
    def from_response(
        cls: Type["InitiatedUploadDTO"], message: pb2.InitiateUploadResponse
    ) -> "InitiatedUploadDTO":
        return cls(
            message.upload_id,
            message.part_size,
            [UploadPartDTO.from_response(part) for part in message.parts],
        )

    def to_schema(
        self, schema: type[file_schemas.InitiatedUpload]
    ) -> file_schemas.InitiatedUpload:
        return schema(
            self.upload_id,
            self.part_size,
            [part.to_schema(file_schemas.UploadPart) for part in self.parts],
        )


@dataclass(slots=True, frozen=True)
class CompletePartDTO(ToRequestMixin):
    part_number: int
    etag: str


@dataclass(slots=True, frozen=True)
class CompleteUploadDTO(ToRequestMixin):
    user_id: str
    upload_id: str
    parts: list[CompletePartDTO]

    def to_request(
        self, message: type[pb2.CompleteUploadRequest]
    ) -> pb2.CompleteUploadRequest:
        return message(
            user_id=self.user_id,
            upload_id=self.upload_id,
            parts=[part.to_request(pb2.CompletePart) for part in self.parts],
        )


@dataclass(slots=True, frozen=True)
class AbortUploadDTO(ToRequestMixin):
    user_id: str
    upload_id: str


@dataclass(slots=True, frozen=True)
class FileDTO(ToRequestMixin):
    user_id: str
    file_id: str


@dataclass(slots=True, frozen=True)
class FileInfoDTO(FromResponseMixin, ToSchemaMixin):
    file_id: str
    name: str
    size: int
    uploaded_at: datetime.datetime


@dataclass(slots=True, frozen=True)
class DeleteDTO(ToRequestMixin):
    user_id: str
    file_ids: list[str]
