import datetime
from typing import Annotated
from uuid import UUID

from msgspec import Meta

from .base import BaseStruct


class UploadFile(BaseStruct):
    name: str
    path: Annotated[
        str,
        Meta(
            pattern=r"^\/([^\/\\]+\/)*$",
            examples=["/", "/path/"],
        ),
    ]
    size: int


class UploadURL(BaseStruct):
    url: str


class FileInfo(BaseStruct):
    file_id: UUID
    name: str
    path: Annotated[
        str,
        Meta(
            pattern=r"^\/([^\/\\]+\/)*$",
            examples=["/", "/path/"],
        ),
    ]
    size: int
    uploaded: datetime.datetime


class FileList(BaseStruct):
    files: tuple[FileInfo]
