from typing import Generator

from proto import files_pb2 as pb2

from .base import RPCBase


class Files(RPCBase):
    @RPCBase.handle_exception
    async def upload_file(self, data: dict[str, str | int]) -> str:
        request = pb2.UploadFileRequest(**data)
        url = await self._stub.UploadFile(request)
        return url.url

    @RPCBase.handle_exception
    async def file_info(self, data: dict[str, str]) -> dict[str, str]:
        request = pb2.FileOperationRequest(**data)
        info = await self._stub.FileInfo(request)
        return self.convert_to_dict(info)

    @RPCBase.handle_exception
    async def file_list(self, user_id: str) -> Generator[dict[str, str], None, None]:
        request = pb2.AllFilesOperationRequest(user_id=user_id)
        files = await self._stub.FileList(request)
        return (self.convert_to_dict(file) for file in files.files)

    @RPCBase.handle_exception
    async def download_file(self, data: dict[str, str]) -> str:
        request = pb2.FileOperationRequest(**data)
        url = await self._stub.DownloadFile(request)
        return url.url

    @RPCBase.handle_exception
    async def delete_files(self, data: dict[str, str]) -> None:
        request = pb2.FilesOperationRequest(**data)
        await self._stub.DeleteFiles(request)

    @RPCBase.handle_exception
    async def delete_all_files(self, user_id: str) -> None:
        request = pb2.AllFilesOperationRequest(user_id=user_id)
        await self._stub.DeleteAllFiles(request)
