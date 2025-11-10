import datetime
from typing import Annotated

from msgspec import Meta, Struct

UUID4_REGEX = r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$"
UUID4_EXAMPLES = ["123e4567-e89b-42d3-a456-426614174000"]


class InitiateUpload(Struct):
    name: Annotated[str, Meta(max_length=255)]
    size: Annotated[int, Meta(gt=0)]


class UploadPart(Struct):
    part_number: Annotated[int, Meta(gt=0)]
    url: str


class InitiatedUpload(Struct):
    upload_id: Annotated[str, Meta(pattern=UUID4_REGEX, examples=UUID4_EXAMPLES)]
    part_size: Annotated[int, Meta(gt=0)]
    parts: list[UploadPart]


class CompletePart(Struct):
    part_number: Annotated[int, Meta(gt=0)]
    etag: str


class CompleteUpload(Struct):
    upload_id: Annotated[str, Meta(pattern=UUID4_REGEX, examples=UUID4_EXAMPLES)]
    parts: list[CompletePart]


class FileInfo(Struct):
    file_id: Annotated[str, Meta(pattern=UUID4_REGEX, examples=UUID4_EXAMPLES)]
    name: Annotated[str, Meta(max_length=255)]
    size: Annotated[int, Meta(gt=0)]
    uploaded_at: datetime.datetime


class FileList(Struct):
    files: tuple[FileInfo, ...]
