import datetime
from dataclasses import dataclass

from .base import BaseResponseDTO


@dataclass(slots=True, frozen=True)
class FileInfoResponseDTO(BaseResponseDTO):
    file_id: str
    user_id: str | None
    name: str
    path: str
    size: int
    uploaded: datetime.datetime


@dataclass(slots=True, frozen=True)
class DeleteFilesResponseDTO(BaseResponseDTO):
    user_id: str
    paths: list[str]
