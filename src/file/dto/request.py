from dataclasses import dataclass

from .base import BaseRequestDTO


@dataclass(slots=True, frozen=True)
class UploadFileRequestDTO(BaseRequestDTO):
    user_id: str
    name: str
    size: str | int


@dataclass(slots=True, frozen=True)
class FileOperationRequestDTO(BaseRequestDTO):
    user_id: str
    file_id: str


@dataclass(slots=True, frozen=True)
class DeleteFilesRequestDTO(BaseRequestDTO):
    user_id: str
    file_ids: list[str]
