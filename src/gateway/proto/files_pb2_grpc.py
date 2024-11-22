# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""

import grpc

from . import files_pb2 as files__pb2

GRPC_GENERATED_VERSION = "1.66.1"
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower

    _version_not_supported = first_version_is_lower(
        GRPC_VERSION, GRPC_GENERATED_VERSION
    )
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f"The grpc package installed is at version {GRPC_VERSION},"
        + " but the generated code in files_pb2_grpc.py depends on"
        + f" grpcio>={GRPC_GENERATED_VERSION}."
        + f" Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}"
        + f" or downgrade your generated code using grpcio-tools<={GRPC_VERSION}."
    )


class FilesStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.UploadFile = channel.stream_unary(
            "/files.Files/UploadFile",
            request_serializer=files__pb2.UploadFileRequest.SerializeToString,
            response_deserializer=files__pb2.Empty.FromString,
            _registered_method=True,
        )
        self.FileInfo = channel.unary_unary(
            "/files.Files/FileInfo",
            request_serializer=files__pb2.FileOperationRequest.SerializeToString,
            response_deserializer=files__pb2.FileInfoResponse.FromString,
            _registered_method=True,
        )
        self.FileList = channel.unary_unary(
            "/files.Files/FileList",
            request_serializer=files__pb2.AllFilesOperationRequest.SerializeToString,
            response_deserializer=files__pb2.FileListResponse.FromString,
            _registered_method=True,
        )
        self.DownloadFile = channel.unary_unary(
            "/files.Files/DownloadFile",
            request_serializer=files__pb2.FileOperationRequest.SerializeToString,
            response_deserializer=files__pb2.DownloadFileResponse.FromString,
            _registered_method=True,
        )
        self.DeleteFiles = channel.unary_unary(
            "/files.Files/DeleteFiles",
            request_serializer=files__pb2.FilesOperationRequest.SerializeToString,
            response_deserializer=files__pb2.Empty.FromString,
            _registered_method=True,
        )
        self.DeleteAllFiles = channel.unary_unary(
            "/files.Files/DeleteAllFiles",
            request_serializer=files__pb2.AllFilesOperationRequest.SerializeToString,
            response_deserializer=files__pb2.Empty.FromString,
            _registered_method=True,
        )


class FilesServicer(object):
    """Missing associated documentation comment in .proto file."""

    def UploadFile(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def FileInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def FileList(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def DownloadFile(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def DeleteFiles(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def DeleteAllFiles(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_FilesServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "UploadFile": grpc.stream_unary_rpc_method_handler(
            servicer.UploadFile,
            request_deserializer=files__pb2.UploadFileRequest.FromString,
            response_serializer=files__pb2.Empty.SerializeToString,
        ),
        "FileInfo": grpc.unary_unary_rpc_method_handler(
            servicer.FileInfo,
            request_deserializer=files__pb2.FileOperationRequest.FromString,
            response_serializer=files__pb2.FileInfoResponse.SerializeToString,
        ),
        "FileList": grpc.unary_unary_rpc_method_handler(
            servicer.FileList,
            request_deserializer=files__pb2.AllFilesOperationRequest.FromString,
            response_serializer=files__pb2.FileListResponse.SerializeToString,
        ),
        "DownloadFile": grpc.unary_unary_rpc_method_handler(
            servicer.DownloadFile,
            request_deserializer=files__pb2.FileOperationRequest.FromString,
            response_serializer=files__pb2.DownloadFileResponse.SerializeToString,
        ),
        "DeleteFiles": grpc.unary_unary_rpc_method_handler(
            servicer.DeleteFiles,
            request_deserializer=files__pb2.FilesOperationRequest.FromString,
            response_serializer=files__pb2.Empty.SerializeToString,
        ),
        "DeleteAllFiles": grpc.unary_unary_rpc_method_handler(
            servicer.DeleteAllFiles,
            request_deserializer=files__pb2.AllFilesOperationRequest.FromString,
            response_serializer=files__pb2.Empty.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "files.Files", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers("files.Files", rpc_method_handlers)


# This class is part of an EXPERIMENTAL API.
class Files(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def UploadFile(
        request_iterator,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.stream_unary(
            request_iterator,
            target,
            "/files.Files/UploadFile",
            files__pb2.UploadFileRequest.SerializeToString,
            files__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )

    @staticmethod
    def FileInfo(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/files.Files/FileInfo",
            files__pb2.FileOperationRequest.SerializeToString,
            files__pb2.FileInfoResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )

    @staticmethod
    def FileList(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/files.Files/FileList",
            files__pb2.AllFilesOperationRequest.SerializeToString,
            files__pb2.FileListResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )

    @staticmethod
    def DownloadFile(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/files.Files/DownloadFile",
            files__pb2.FileOperationRequest.SerializeToString,
            files__pb2.DownloadFileResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )

    @staticmethod
    def DeleteFiles(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/files.Files/DeleteFiles",
            files__pb2.FilesOperationRequest.SerializeToString,
            files__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )

    @staticmethod
    def DeleteAllFiles(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/files.Files/DeleteAllFiles",
            files__pb2.AllFilesOperationRequest.SerializeToString,
            files__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )
