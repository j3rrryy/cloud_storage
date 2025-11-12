from dataclasses import dataclass
from typing import Type, cast

from proto import file_pb2 as pb2

from .base import BaseRequestDTO, Message


@dataclass(slots=True, frozen=True)
class InitiateUploadRequestDTO(BaseRequestDTO):
    user_id: str
    name: str
    size: int

    @classmethod
    def from_request(
        cls: Type["InitiateUploadRequestDTO"], request: Message
    ) -> "InitiateUploadRequestDTO":
        request_ = cast(pb2.InitiateUploadRequest, request)
        return cls(request_.user_id, request_.name, int(request_.size))


@dataclass(slots=True, frozen=True)
class InitiatedUploadRequestDTO(BaseRequestDTO):
    file_id: str
    user_id: str
    name: str
    size: int


@dataclass(slots=True, frozen=True)
class CompletePartRequestDTO(BaseRequestDTO):
    part_number: int
    etag: str


@dataclass(slots=True, frozen=True)
class CompleteUploadRequestDTO(BaseRequestDTO):
    user_id: str
    upload_id: str
    parts: list[CompletePartRequestDTO]

    @classmethod
    def from_request(
        cls: Type["CompleteUploadRequestDTO"], request: Message
    ) -> "CompleteUploadRequestDTO":
        request_ = cast(pb2.CompleteUploadRequest, request)
        return cls(
            request_.user_id,
            request_.upload_id,
            [CompletePartRequestDTO.from_request(part) for part in request_.parts],
        )


@dataclass(slots=True, frozen=True)
class AbortUploadRequestDTO(BaseRequestDTO):
    user_id: str
    upload_id: str


@dataclass(slots=True, frozen=True)
class FileRequestDTO(BaseRequestDTO):
    user_id: str
    file_id: str


@dataclass(slots=True, frozen=True)
class DeleteFilesRequestDTO(BaseRequestDTO):
    user_id: str
    file_ids: list[str]
