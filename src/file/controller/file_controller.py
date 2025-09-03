from google.protobuf import empty_pb2

from dto import request as request_dto
from proto import FileServicer
from proto import file_pb2 as pb2
from service import FileService
from utils import ExceptionHandler


class FileController(FileServicer):
    async def Register(self, request, context):
        await ExceptionHandler.handle(context, FileService.register, request.user_id)

    async def DeleteProfile(self, request, context):
        await ExceptionHandler.handle(
            context, FileService.delete_profile, request.user_id
        )

    async def CreateFolder(self, request, context): ...
    async def ListFolder(self, request, context): ...
    async def RenameFolder(self, request, context): ...
    async def MoveFolder(self, request, context): ...
    async def DeleteFolders(self, request, context): ...

    async def UploadFile(self, request, context):
        dto = request_dto.UploadFileRequestDTO.from_request(request)
        upload_url = await ExceptionHandler.handle(
            context, FileService.upload_file, dto
        )
        return pb2.FileURL(url=upload_url)

    async def DownloadFile(self, request, context):
        dto = request_dto.FileOperationRequestDTO.from_request(request)
        file_url = await ExceptionHandler.handle(
            context, FileService.download_file, dto
        )
        return pb2.FileURLResponse(url=file_url)

    async def RenameFile(self, request, context): ...
    async def MoveFile(self, request, context): ...

    async def DeleteFiles(self, request, context):
        dto = request_dto.DeleteFilesRequestDTO.from_request(request)
        await ExceptionHandler.handle(context, FileService.delete_files, dto)
        return empty_pb2.Empty()
