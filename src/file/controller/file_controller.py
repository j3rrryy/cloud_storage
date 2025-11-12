from google.protobuf import empty_pb2

from dto import request as request_dto
from proto import FileServicer
from proto import file_pb2 as pb2
from service import FileService
from utils import ExceptionHandler


class FileController(FileServicer):
    async def InitiateUpload(self, request, context):
        dto = request_dto.InitiateUploadRequestDTO.from_request(request)
        upload = await ExceptionHandler.handle(
            context, FileService.initiate_upload, dto
        )
        return upload.to_response(pb2.InitiateUploadResponse)

    async def CompleteUpload(self, request, context):
        dto = request_dto.CompleteUploadRequestDTO.from_request(request)
        await ExceptionHandler.handle(context, FileService.complete_upload, dto)
        return empty_pb2.Empty()

    async def AbortUpload(self, request, context):
        dto = request_dto.AbortUploadRequestDTO.from_request(request)
        await ExceptionHandler.handle(context, FileService.abort_upload, dto)
        return empty_pb2.Empty()

    async def FileInfo(self, request, context):
        dto = request_dto.FileRequestDTO.from_request(request)
        info = await ExceptionHandler.handle(context, FileService.file_info, dto)
        return info.to_response(pb2.FileInfoResponse)

    async def FileList(self, request, context):
        files = await ExceptionHandler.handle(
            context, FileService.file_list, request.user_id
        )
        return pb2.FileListResponse(
            files=(file.to_response(pb2.FileInfoResponse) for file in files)
        )

    async def Download(self, request, context):
        dto = request_dto.FileRequestDTO.from_request(request)
        file_url = await ExceptionHandler.handle(context, FileService.download, dto)
        return pb2.URL(url=file_url)

    async def Delete(self, request, context):
        dto = request_dto.DeleteFilesRequestDTO.from_request(request)
        await ExceptionHandler.handle(context, FileService.delete, dto)
        return empty_pb2.Empty()

    async def DeleteAll(self, request, context):
        await ExceptionHandler.handle(context, FileService.delete_all, request.user_id)
        return empty_pb2.Empty()
