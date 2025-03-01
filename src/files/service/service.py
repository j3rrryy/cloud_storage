from google.protobuf import empty_pb2

import proto
from config import load_config
from controllers import DatabaseController as DBC
from controllers import StorageController as STC
from dto import request as request_dto
from proto import files_pb2 as pb2
from utils import ExceptionHandler


class FilesServicer(proto.FilesServicer):
    _eh = ExceptionHandler(load_config().app.logger)

    async def UploadFile(self, request, context):
        dto = request_dto.UploadFileRequestDTO.from_request(request)
        await self._eh(context, DBC.upload_file, dto)
        upload_url = await self._eh(context, STC.upload_file, dto)
        return pb2.FileURLResponse(url=upload_url)

    async def FileInfo(self, request, context):
        dto = request_dto.FileOperationRequestDTO.from_request(request)
        info = await self._eh(context, DBC.file_info, dto)
        return pb2.FileInfoResponse(**info.dict())

    async def FileList(self, request, context):
        files = await self._eh(context, DBC.file_list, request.user_id)
        return pb2.FileListResponse(
            files=(pb2.FileInfoResponse(**file.dict()) for file in files)
        )

    async def DownloadFile(self, request, context):
        dto = request_dto.FileOperationRequestDTO.from_request(request)
        info = await self._eh(context, DBC.download_file, dto)
        file_url = await self._eh(context, STC.download_file, info)
        return pb2.FileURLResponse(url=file_url)

    async def DeleteFiles(self, request, context):
        dto = request_dto.DeleteFilesRequestDTO.from_request(request)
        files = await self._eh(context, DBC.delete_files, dto)
        await self._eh(context, STC.delete_files, files)
        return empty_pb2.Empty()

    async def DeleteAllFiles(self, request, context):
        await self._eh(context, STC.delete_all_files, request.user_id)
        await self._eh(context, DBC.delete_all_files, request.user_id)
        return empty_pb2.Empty()
