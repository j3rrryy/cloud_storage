import datetime
from uuid import UUID

from .base import BaseStruct


class Filename(BaseStruct):
    name: str


class UploadURL(BaseStruct):
    url: str


class ConfirmUpload(BaseStruct):
    name: str
    size: int


class FileInfo(BaseStruct):
    file_id: UUID
    name: str
    size: int
    uploaded: datetime.datetime


class FileList(BaseStruct):
    files: tuple[FileInfo]
