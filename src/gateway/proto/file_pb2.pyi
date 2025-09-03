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

class UserId(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class CreateFolderRequest(_message.Message):
    __slots__ = ("folder", "name")
    FOLDER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    folder: FolderRef
    name: str
    def __init__(
        self,
        folder: _Optional[_Union[FolderRef, _Mapping]] = ...,
        name: _Optional[str] = ...,
    ) -> None: ...

class FolderRef(_message.Message):
    __slots__ = ("user_id", "folder_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    folder_id: str
    def __init__(
        self, user_id: _Optional[str] = ..., folder_id: _Optional[str] = ...
    ) -> None: ...

class ListFolderRequest(_message.Message):
    __slots__ = ("folder", "page_size", "cursor")
    FOLDER_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    folder: FolderRef
    page_size: int
    cursor: str
    def __init__(
        self,
        folder: _Optional[_Union[FolderRef, _Mapping]] = ...,
        page_size: _Optional[int] = ...,
        cursor: _Optional[str] = ...,
    ) -> None: ...

class ListFolderResponse(_message.Message):
    __slots__ = ("entries", "next_cursor")
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    NEXT_CURSOR_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[Entry]
    next_cursor: str
    def __init__(
        self,
        entries: _Optional[_Iterable[_Union[Entry, _Mapping]]] = ...,
        next_cursor: _Optional[str] = ...,
    ) -> None: ...

class Entry(_message.Message):
    __slots__ = ("id", "name", "file_data", "folder_data")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FILE_DATA_FIELD_NUMBER: _ClassVar[int]
    FOLDER_DATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    file_data: FileData
    folder_data: FolderData
    def __init__(
        self,
        id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        file_data: _Optional[_Union[FileData, _Mapping]] = ...,
        folder_data: _Optional[_Union[FolderData, _Mapping]] = ...,
    ) -> None: ...

class FolderData(_message.Message):
    __slots__ = ("parent_id",)
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    parent_id: str
    def __init__(self, parent_id: _Optional[str] = ...) -> None: ...

class FileData(_message.Message):
    __slots__ = ("size", "uploaded_at", "updated_at")
    SIZE_FIELD_NUMBER: _ClassVar[int]
    UPLOADED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    size: int
    uploaded_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        size: _Optional[int] = ...,
        uploaded_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        updated_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
    ) -> None: ...

class RenameFolderRequest(_message.Message):
    __slots__ = ("folder", "new_name")
    FOLDER_FIELD_NUMBER: _ClassVar[int]
    NEW_NAME_FIELD_NUMBER: _ClassVar[int]
    folder: FolderRef
    new_name: str
    def __init__(
        self,
        folder: _Optional[_Union[FolderRef, _Mapping]] = ...,
        new_name: _Optional[str] = ...,
    ) -> None: ...

class MoveFolderRequest(_message.Message):
    __slots__ = ("folder", "new_parent_folder_id")
    FOLDER_FIELD_NUMBER: _ClassVar[int]
    NEW_PARENT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    folder: FolderRef
    new_parent_folder_id: str
    def __init__(
        self,
        folder: _Optional[_Union[FolderRef, _Mapping]] = ...,
        new_parent_folder_id: _Optional[str] = ...,
    ) -> None: ...

class DeleteFoldersRequest(_message.Message):
    __slots__ = ("user_id", "folder_ids")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    FOLDER_IDS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    folder_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self, user_id: _Optional[str] = ..., folder_ids: _Optional[_Iterable[str]] = ...
    ) -> None: ...

class UploadFileRequest(_message.Message):
    __slots__ = ("folder", "name", "size")
    FOLDER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    folder: FolderRef
    name: str
    size: int
    def __init__(
        self,
        folder: _Optional[_Union[FolderRef, _Mapping]] = ...,
        name: _Optional[str] = ...,
        size: _Optional[int] = ...,
    ) -> None: ...

class FileURL(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...

class FileRef(_message.Message):
    __slots__ = ("folder", "file_id")
    FOLDER_FIELD_NUMBER: _ClassVar[int]
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    folder: FolderRef
    file_id: str
    def __init__(
        self,
        folder: _Optional[_Union[FolderRef, _Mapping]] = ...,
        file_id: _Optional[str] = ...,
    ) -> None: ...

class RenameFileRequest(_message.Message):
    __slots__ = ("file", "new_name")
    FILE_FIELD_NUMBER: _ClassVar[int]
    NEW_NAME_FIELD_NUMBER: _ClassVar[int]
    file: FileRef
    new_name: str
    def __init__(
        self,
        file: _Optional[_Union[FileRef, _Mapping]] = ...,
        new_name: _Optional[str] = ...,
    ) -> None: ...

class MoveFileRequest(_message.Message):
    __slots__ = ("file", "new_folder_id")
    FILE_FIELD_NUMBER: _ClassVar[int]
    NEW_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    file: FileRef
    new_folder_id: str
    def __init__(
        self,
        file: _Optional[_Union[FileRef, _Mapping]] = ...,
        new_folder_id: _Optional[str] = ...,
    ) -> None: ...

class DeleteFilesRequest(_message.Message):
    __slots__ = ("user_id", "file_ids")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_IDS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    file_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self, user_id: _Optional[str] = ..., file_ids: _Optional[_Iterable[str]] = ...
    ) -> None: ...
