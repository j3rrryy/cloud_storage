from typing import Generator

from dto import file as file_dto
from proto import file_pb2 as pb2

from .base import RPCBase


class File(RPCBase):
    @RPCBase.handle_exception
    async def upload_file(self, data: file_dto.UploadFileDTO) -> str:
        request = pb2.UploadFileRequest(**data.dict())
        url = await self._stub.UploadFile(request)
        return url.url

    @RPCBase.handle_exception
    async def file_info(self, data: file_dto.FileDTO) -> file_dto.FileInfoDTO:
        request = pb2.FileOperationRequest(**data.dict())
        file_info = await self._stub.FileInfo(request)
        return self.convert_to_dto(file_info, file_dto.FileInfoDTO)

    @RPCBase.handle_exception
    async def file_list(
        self, user_id: str
    ) -> Generator[file_dto.FileInfoDTO, None, None]:
        request = pb2.UserId(user_id=user_id)
        files = await self._stub.FileList(request)
        return (self.convert_to_dto(file, file_dto.FileInfoDTO) for file in files.files)

    @RPCBase.handle_exception
    async def download_file(self, data: file_dto.FileDTO) -> str:
        request = pb2.FileOperationRequest(**data.dict())
        url = await self._stub.DownloadFile(request)
        return url.url

    @RPCBase.handle_exception
    async def delete_files(self, data: file_dto.DeleteFilesDTO) -> None:
        request = pb2.DeleteFilesRequest(**data.dict())
        await self._stub.DeleteFiles(request)

    @RPCBase.handle_exception
    async def delete_all_files(self, user_id: str) -> None:
        request = pb2.UserId(user_id=user_id)
        await self._stub.DeleteAllFiles(request)
