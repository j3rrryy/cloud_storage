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
    b'\n\x0b\x66iles.proto\x12\x05\x66iles\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1fgoogle/protobuf/timestamp.proto"7\n\x12\x44\x65leteFilesRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x10\n\x08\x66ile_ids\x18\x02 \x03(\t"{\n\x10\x46ileInfoResponse\x12\x0f\n\x07\x66ile_id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04path\x18\x03 \x01(\t\x12\x0c\n\x04size\x18\x04 \x01(\x04\x12,\n\x08uploaded\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.Timestamp":\n\x10\x46ileListResponse\x12&\n\x05\x66iles\x18\x01 \x03(\x0b\x32\x17.files.FileInfoResponse"8\n\x14\x46ileOperationRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x0f\n\x07\x66ile_id\x18\x02 \x01(\t"\x1e\n\x0f\x46ileURLResponse\x12\x0b\n\x03url\x18\x01 \x01(\t"N\n\x11UploadFileRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04path\x18\x03 \x01(\t\x12\x0c\n\x04size\x18\x04 \x01(\x04"\x19\n\x06UserId\x12\x0f\n\x07user_id\x18\x01 \x01(\t2\xfd\x02\n\x05\x46iles\x12>\n\nUploadFile\x12\x18.files.UploadFileRequest\x1a\x16.files.FileURLResponse\x12@\n\x08\x46ileInfo\x12\x1b.files.FileOperationRequest\x1a\x17.files.FileInfoResponse\x12\x32\n\x08\x46ileList\x12\r.files.UserId\x1a\x17.files.FileListResponse\x12\x43\n\x0c\x44ownloadFile\x12\x1b.files.FileOperationRequest\x1a\x16.files.FileURLResponse\x12@\n\x0b\x44\x65leteFiles\x12\x19.files.DeleteFilesRequest\x1a\x16.google.protobuf.Empty\x12\x37\n\x0e\x44\x65leteAllFiles\x12\r.files.UserId\x1a\x16.google.protobuf.Emptyb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "files_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_DELETEFILESREQUEST"]._serialized_start = 84
    _globals["_DELETEFILESREQUEST"]._serialized_end = 139
    _globals["_FILEINFORESPONSE"]._serialized_start = 141
    _globals["_FILEINFORESPONSE"]._serialized_end = 264
    _globals["_FILELISTRESPONSE"]._serialized_start = 266
    _globals["_FILELISTRESPONSE"]._serialized_end = 324
    _globals["_FILEOPERATIONREQUEST"]._serialized_start = 326
    _globals["_FILEOPERATIONREQUEST"]._serialized_end = 382
    _globals["_FILEURLRESPONSE"]._serialized_start = 384
    _globals["_FILEURLRESPONSE"]._serialized_end = 414
    _globals["_UPLOADFILEREQUEST"]._serialized_start = 416
    _globals["_UPLOADFILEREQUEST"]._serialized_end = 494
    _globals["_USERID"]._serialized_start = 496
    _globals["_USERID"]._serialized_end = 521
    _globals["_FILES"]._serialized_start = 524
    _globals["_FILES"]._serialized_end = 905
# @@protoc_insertion_point(module_scope)
