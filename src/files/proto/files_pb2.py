# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: files.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC, 5, 29, 0, "", "files.proto"
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0b\x66iles.proto\x12\x05\x66iles\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1fgoogle/protobuf/timestamp.proto"+\n\x18\x41llFilesOperationRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t"m\n\x10\x46ileInfoResponse\x12\x0f\n\x07\x66ile_id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04size\x18\x03 \x01(\x04\x12,\n\x08uploaded\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp":\n\x10\x46ileListResponse\x12&\n\x05\x66iles\x18\x01 \x03(\x0b\x32\x17.files.FileInfoResponse"8\n\x14\x46ileOperationRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x0f\n\x07\x66ile_id\x18\x02 \x01(\t":\n\x15\x46ilesOperationRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x10\n\x08\x66ile_ids\x18\x02 \x03(\t"\x1e\n\x0f\x46ileURLResponse\x12\x0b\n\x03url\x18\x01 \x01(\t"2\n\x11UploadFileRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t"!\n\x12UploadFileResponse\x12\x0b\n\x03url\x18\x01 \x01(\t"C\n\x14\x43onfirmUploadRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04size\x18\x03 \x01(\x04\x32\xed\x03\n\x05\x46iles\x12\x41\n\nUploadFile\x12\x18.files.UploadFileRequest\x1a\x19.files.UploadFileResponse\x12\x44\n\rConfirmUpload\x12\x1b.files.ConfirmUploadRequest\x1a\x16.google.protobuf.Empty\x12@\n\x08\x46ileInfo\x12\x1b.files.FileOperationRequest\x1a\x17.files.FileInfoResponse\x12\x44\n\x08\x46ileList\x12\x1f.files.AllFilesOperationRequest\x1a\x17.files.FileListResponse\x12\x43\n\x0c\x44ownloadFile\x12\x1b.files.FileOperationRequest\x1a\x16.files.FileURLResponse\x12\x43\n\x0b\x44\x65leteFiles\x12\x1c.files.FilesOperationRequest\x1a\x16.google.protobuf.Empty\x12I\n\x0e\x44\x65leteAllFiles\x12\x1f.files.AllFilesOperationRequest\x1a\x16.google.protobuf.Emptyb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "files_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_ALLFILESOPERATIONREQUEST"]._serialized_start = 84
    _globals["_ALLFILESOPERATIONREQUEST"]._serialized_end = 127
    _globals["_FILEINFORESPONSE"]._serialized_start = 129
    _globals["_FILEINFORESPONSE"]._serialized_end = 238
    _globals["_FILELISTRESPONSE"]._serialized_start = 240
    _globals["_FILELISTRESPONSE"]._serialized_end = 298
    _globals["_FILEOPERATIONREQUEST"]._serialized_start = 300
    _globals["_FILEOPERATIONREQUEST"]._serialized_end = 356
    _globals["_FILESOPERATIONREQUEST"]._serialized_start = 358
    _globals["_FILESOPERATIONREQUEST"]._serialized_end = 416
    _globals["_FILEURLRESPONSE"]._serialized_start = 418
    _globals["_FILEURLRESPONSE"]._serialized_end = 448
    _globals["_UPLOADFILEREQUEST"]._serialized_start = 450
    _globals["_UPLOADFILEREQUEST"]._serialized_end = 500
    _globals["_UPLOADFILERESPONSE"]._serialized_start = 502
    _globals["_UPLOADFILERESPONSE"]._serialized_end = 535
    _globals["_CONFIRMUPLOADREQUEST"]._serialized_start = 537
    _globals["_CONFIRMUPLOADREQUEST"]._serialized_end = 604
    _globals["_FILES"]._serialized_start = 607
    _globals["_FILES"]._serialized_end = 1100
# @@protoc_insertion_point(module_scope)
