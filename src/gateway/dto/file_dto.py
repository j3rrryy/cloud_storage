import datetime
from dataclasses import dataclass

from .base_dto import FromResponseMixin, ToRequestMixin, ToSchemaMixin


@dataclass(slots=True, frozen=True)
class UploadFileDTO(ToRequestMixin):
    user_id: str
    name: str
    path: str
    size: int


@dataclass(slots=True, frozen=True)
class FileDTO(ToRequestMixin):
    user_id: str
    file_id: str


@dataclass(slots=True, frozen=True)
class FileInfoDTO(FromResponseMixin, ToSchemaMixin):
    file_id: str
    name: str
    path: str
    size: int
    uploaded: datetime.datetime


@dataclass(slots=True, frozen=True)
class DeleteFilesDTO(ToRequestMixin):
    user_id: str
    file_ids: set[str]
