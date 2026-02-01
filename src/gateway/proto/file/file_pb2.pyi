import datetime
from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import message as _message
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class InitiateUploadRequest(_message.Message):
    __slots__ = ("user_id", "name", "size")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    name: str
    size: int
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        size: _Optional[int] = ...,
    ) -> None: ...

class InitiateUploadResponse(_message.Message):
    __slots__ = ("upload_id", "part_size", "parts")
    UPLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    PART_SIZE_FIELD_NUMBER: _ClassVar[int]
    PARTS_FIELD_NUMBER: _ClassVar[int]
    upload_id: str
    part_size: int
    parts: _containers.RepeatedCompositeFieldContainer[UploadPart]
    def __init__(
        self,
        upload_id: _Optional[str] = ...,
        part_size: _Optional[int] = ...,
        parts: _Optional[_Iterable[_Union[UploadPart, _Mapping]]] = ...,
    ) -> None: ...

class UploadPart(_message.Message):
    __slots__ = ("part_number", "url")
    PART_NUMBER_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    part_number: int
    url: str
    def __init__(
        self, part_number: _Optional[int] = ..., url: _Optional[str] = ...
    ) -> None: ...

class CompleteUploadRequest(_message.Message):
    __slots__ = ("user_id", "upload_id", "parts")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    PARTS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    upload_id: str
    parts: _containers.RepeatedCompositeFieldContainer[CompletePart]
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        upload_id: _Optional[str] = ...,
        parts: _Optional[_Iterable[_Union[CompletePart, _Mapping]]] = ...,
    ) -> None: ...

class CompletePart(_message.Message):
    __slots__ = ("part_number", "etag")
    PART_NUMBER_FIELD_NUMBER: _ClassVar[int]
    ETAG_FIELD_NUMBER: _ClassVar[int]
    part_number: int
    etag: str
    def __init__(
        self, part_number: _Optional[int] = ..., etag: _Optional[str] = ...
    ) -> None: ...

class AbortUploadRequest(_message.Message):
    __slots__ = ("user_id", "upload_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    upload_id: str
    def __init__(
        self, user_id: _Optional[str] = ..., upload_id: _Optional[str] = ...
    ) -> None: ...

class UserId(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class FileListResponse(_message.Message):
    __slots__ = ("files",)
    FILES_FIELD_NUMBER: _ClassVar[int]
    files: _containers.RepeatedCompositeFieldContainer[FileInfo]
    def __init__(
        self, files: _Optional[_Iterable[_Union[FileInfo, _Mapping]]] = ...
    ) -> None: ...

class FileInfo(_message.Message):
    __slots__ = ("file_id", "name", "size", "uploaded_at")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    UPLOADED_AT_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    name: str
    size: int
    uploaded_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        file_id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        size: _Optional[int] = ...,
        uploaded_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
    ) -> None: ...

class FileRequest(_message.Message):
    __slots__ = ("user_id", "file_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    file_id: str
    def __init__(
        self, user_id: _Optional[str] = ..., file_id: _Optional[str] = ...
    ) -> None: ...

class URL(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...

class DeleteRequest(_message.Message):
    __slots__ = ("user_id", "file_ids")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_IDS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    file_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self, user_id: _Optional[str] = ..., file_ids: _Optional[_Iterable[str]] = ...
    ) -> None: ...
