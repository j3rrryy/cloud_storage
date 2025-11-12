from dto import file_dto
from proto import file_pb2 as pb2

from .base_service import RPCBaseService


class FileService(RPCBaseService):
    @RPCBaseService.exception_handler
    async def initiate_upload(
        self, data: file_dto.InitiateUploadDTO
    ) -> file_dto.InitiatedUploadDTO:
        request = data.to_request(pb2.InitiateUploadRequest)
        upload: pb2.InitiateUploadResponse = await self._stub.InitiateUpload(request)
        return file_dto.InitiatedUploadDTO.from_response(upload)

    @RPCBaseService.exception_handler
    async def complete_upload(self, data: file_dto.CompleteUploadDTO) -> None:
        request = data.to_request(pb2.CompleteUploadRequest)
        await self._stub.CompleteUpload(request)

    @RPCBaseService.exception_handler
    async def abort_upload(self, data: file_dto.AbortUploadDTO) -> None:
        request = data.to_request(pb2.AbortUploadRequest)
        await self._stub.AbortUpload(request)

    @RPCBaseService.exception_handler
    async def file_info(self, data: file_dto.FileDTO) -> file_dto.FileInfoDTO:
        request = data.to_request(pb2.FileRequest)
        file_info: pb2.FileInfoResponse = await self._stub.FileInfo(request)
        return file_dto.FileInfoDTO.from_response(file_info)

    @RPCBaseService.exception_handler
    async def file_list(self, user_id: str) -> list[file_dto.FileInfoDTO]:
        request = pb2.UserId(user_id=user_id)
        files: pb2.FileListResponse = await self._stub.FileList(request)
        return [file_dto.FileInfoDTO.from_response(file) for file in files.files]

    @RPCBaseService.exception_handler
    async def download(self, data: file_dto.FileDTO) -> str:
        request = data.to_request(pb2.FileRequest)
        url: pb2.URL = await self._stub.Download(request)
        return url.url

    @RPCBaseService.exception_handler
    async def delete(self, data: file_dto.DeleteDTO) -> None:
        if not data.file_ids:
            return
        request = data.to_request(pb2.DeleteRequest)
        await self._stub.Delete(request)

    @RPCBaseService.exception_handler
    async def delete_all(self, user_id: str) -> None:
        request = pb2.UserId(user_id=user_id)
        await self._stub.DeleteAll(request)
