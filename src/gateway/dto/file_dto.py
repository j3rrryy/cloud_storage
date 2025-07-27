import datetime
from dataclasses import dataclass

from .base_dto import BaseDTO


@dataclass(slots=True, frozen=True)
class UploadFileDTO(BaseDTO):
    user_id: str
    name: str
    path: str
    size: int


@dataclass(slots=True, frozen=True)
class FileDTO(BaseDTO):
    user_id: str
    file_id: str


@dataclass(slots=True, frozen=True)
class FileInfoDTO(BaseDTO):
    file_id: str
    name: str
    path: str
    size: int
    uploaded: datetime.datetime


@dataclass(slots=True, frozen=True)
class DeleteFilesDTO(BaseDTO):
    user_id: str
    file_ids: set[str]
