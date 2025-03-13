from google.protobuf import empty_pb2

from config import load_config
from dto import request as request_dto
from proto import FileServicer
from proto import file_pb2 as pb2
from service import FileService
from utils import ExceptionHandler


class FileController(FileServicer):
    _eh = ExceptionHandler(load_config().app.logger)

    async def UploadFile(self, request, context):
        dto = request_dto.UploadFileRequestDTO.from_request(request)
        upload_url = await self._eh(context, FileService.upload_file, dto)
        return pb2.FileURLResponse(url=upload_url)

    async def FileInfo(self, request, context):
        dto = request_dto.FileOperationRequestDTO.from_request(request)
        info = await self._eh(context, FileService.file_info, dto)
        return pb2.FileInfoResponse(**info.dict())

    async def FileList(self, request, context):
        files = await self._eh(context, FileService.file_list, request.user_id)
        return pb2.FileListResponse(
            files=(pb2.FileInfoResponse(**file.dict()) for file in files)
        )

    async def DownloadFile(self, request, context):
        dto = request_dto.FileOperationRequestDTO.from_request(request)
        file_url = await self._eh(context, FileService.download_file, dto)
        return pb2.FileURLResponse(url=file_url)

    async def DeleteFiles(self, request, context):
        dto = request_dto.DeleteFilesRequestDTO.from_request(request)
        await self._eh(context, FileService.delete_files, dto)
        return empty_pb2.Empty()

    async def DeleteAllFiles(self, request, context):
        await self._eh(context, FileService.delete_all_files, request.user_id)
        return empty_pb2.Empty()
