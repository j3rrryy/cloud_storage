from .base import BaseStruct


class FileInfo(BaseStruct):
    file_id: str
    name: str
    size: str
    uploaded: str


class FileList(BaseStruct):
    files: tuple[FileInfo]


class FileURL(BaseStruct):
    url: str
