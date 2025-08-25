from typing import Generator

from dto import file_dto
from proto import file_pb2 as pb2

from .base_service import RPCBaseService


class FileService(RPCBaseService):
    @RPCBaseService.exception_handler
    async def upload_file(self, data: file_dto.UploadFileDTO) -> str:
        request = data.to_request(pb2.UploadFileRequest)
        url: pb2.FileURLResponse = await self._stub.UploadFile(request)
        return url.url

    @RPCBaseService.exception_handler
    async def file_info(self, data: file_dto.FileDTO) -> file_dto.FileInfoDTO:
        request = data.to_request(pb2.FileOperationRequest)
        file_info: pb2.FileInfoResponse = await self._stub.FileInfo(request)
        return file_dto.FileInfoDTO.from_response(file_info)

    @RPCBaseService.exception_handler
    async def file_list(
        self, user_id: str
    ) -> Generator[file_dto.FileInfoDTO, None, None]:
        request = pb2.UserId(user_id=user_id)
        files: pb2.FileListResponse = await self._stub.FileList(request)
        return (file_dto.FileInfoDTO.from_response(file) for file in files.files)

    @RPCBaseService.exception_handler
    async def download_file(self, data: file_dto.FileDTO) -> str:
        request = data.to_request(pb2.FileOperationRequest)
        url: pb2.FileURLResponse = await self._stub.DownloadFile(request)
        return url.url

    @RPCBaseService.exception_handler
    async def delete_files(self, data: file_dto.DeleteFilesDTO) -> None:
        request = data.to_request(pb2.DeleteFilesRequest)
        await self._stub.DeleteFiles(request)

    @RPCBaseService.exception_handler
    async def delete_all_files(self, user_id: str) -> None:
        request = pb2.UserId(user_id=user_id)
        await self._stub.DeleteAllFiles(request)
