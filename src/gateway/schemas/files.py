from uuid import UUID

from .base import BaseStruct


class FileInfo(BaseStruct):
    file_id: UUID
    name: str
    size: int
    uploaded: str


class FileList(BaseStruct):
    files: tuple[FileInfo]
