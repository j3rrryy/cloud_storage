import datetime
from typing import Annotated

from msgspec import Meta, Struct

PATH_REGEX = r"^\/([^\/\\]+\/)*$"
PATH_EXAMPLES = ["/", "/path/"]

UUID4_REGEX = r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$"
UUID4_EXAMPLES = ["123e4567-e89b-12d3-a456-426614174000"]


class UploadFile(Struct):
    name: Annotated[str, Meta(max_length=255)]
    path: Annotated[
        str, Meta(pattern=PATH_REGEX, max_length=257, examples=PATH_EXAMPLES)
    ]
    size: int


class UploadURL(Struct):
    url: str


class FileInfo(Struct):
    file_id: Annotated[str, Meta(pattern=UUID4_REGEX, examples=UUID4_EXAMPLES)]
    name: Annotated[str, Meta(max_length=255)]
    path: Annotated[
        str, Meta(pattern=PATH_REGEX, max_length=257, examples=PATH_EXAMPLES)
    ]
    size: int
    uploaded_at: datetime.datetime


class FileList(Struct):
    files: tuple[FileInfo, ...]
