from google.protobuf import empty_pb2

from dto import request as request_dto
from proto import FileServicer
from proto import file_pb2 as pb2
from protocols import FileServiceProtocol


class FileController(FileServicer):
    def __init__(self, file_service: FileServiceProtocol):
        self._file_service = file_service

    async def InitiateUpload(self, request, context):
        dto = request_dto.InitiateUploadRequestDTO.from_request(request)
        upload = await self._file_service.initiate_upload(dto)
        return upload.to_response(pb2.InitiateUploadResponse)

    async def CompleteUpload(self, request, context):
        dto = request_dto.CompleteUploadRequestDTO.from_request(request)
        await self._file_service.complete_upload(dto)
        return empty_pb2.Empty()

    async def AbortUpload(self, request, context):
        dto = request_dto.AbortUploadRequestDTO.from_request(request)
        await self._file_service.abort_upload(dto)
        return empty_pb2.Empty()

    async def FileList(self, request, context):
        files = await self._file_service.file_list(request.user_id)
        return pb2.FileListResponse(
            files=(file.to_response(pb2.FileInfo) for file in files)
        )

    async def Download(self, request, context):
        dto = request_dto.FileRequestDTO.from_request(request)
        file_url = await self._file_service.download(dto)
        return pb2.URL(url=file_url)

    async def Delete(self, request, context):
        dto = request_dto.DeleteFilesRequestDTO.from_request(request)
        await self._file_service.delete(dto)
        return empty_pb2.Empty()

    async def DeleteAll(self, request, context):
        await self._file_service.delete_all(request.user_id)
        return empty_pb2.Empty()
