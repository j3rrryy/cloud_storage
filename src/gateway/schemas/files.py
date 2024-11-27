import datetime
from uuid import UUID

from .base import BaseStruct


class FileInfo(BaseStruct):
    file_id: UUID
    name: str
    size: int
    uploaded: datetime.datetime


class FileList(BaseStruct):
    files: tuple[FileInfo]
