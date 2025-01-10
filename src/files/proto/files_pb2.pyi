from typing import ClassVar as _ClassVar
from typing import Iterable as _Iterable
from typing import Mapping as _Mapping
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import message as _message
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class AllFilesOperationRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class FileInfoResponse(_message.Message):
    __slots__ = ("file_id", "name", "size", "uploaded")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    UPLOADED_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    name: str
    size: int
    uploaded: _timestamp_pb2.Timestamp
    def __init__(
        self,
        file_id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        size: _Optional[int] = ...,
        uploaded: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class FileListResponse(_message.Message):
    __slots__ = ("files",)
    FILES_FIELD_NUMBER: _ClassVar[int]
    files: _containers.RepeatedCompositeFieldContainer[FileInfoResponse]
    def __init__(
        self, files: _Optional[_Iterable[_Union[FileInfoResponse, _Mapping]]] = ...
    ) -> None: ...

class FileOperationRequest(_message.Message):
    __slots__ = ("user_id", "file_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    file_id: str
    def __init__(
        self, user_id: _Optional[str] = ..., file_id: _Optional[str] = ...
    ) -> None: ...

class FilesOperationRequest(_message.Message):
    __slots__ = ("user_id", "file_ids")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_IDS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    file_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self, user_id: _Optional[str] = ..., file_ids: _Optional[_Iterable[str]] = ...
    ) -> None: ...

class FileURLResponse(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...

class UploadFileRequest(_message.Message):
    __slots__ = ("user_id", "name", "chunk")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CHUNK_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    name: str
    chunk: bytes
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        chunk: _Optional[bytes] = ...,
    ) -> None: ...
