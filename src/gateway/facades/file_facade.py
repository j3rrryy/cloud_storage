from dto import file_dto
from protocols import FileServiceProtocol


class FileFacade:
    def __init__(self, file_service: FileServiceProtocol):
        self.file_service = file_service

    async def initiate_upload(
        self, data: file_dto.InitiateUploadDTO
    ) -> file_dto.InitiatedUploadDTO:
        return await self.file_service.initiate_upload(data)

    async def complete_upload(self, data: file_dto.CompleteUploadDTO) -> None:
        await self.file_service.complete_upload(data)

    async def abort_upload(self, data: file_dto.AbortUploadDTO) -> None:
        await self.file_service.abort_upload(data)

    async def file_info(self, data: file_dto.FileDTO) -> file_dto.FileInfoDTO:
        return await self.file_service.file_info(data)

    async def file_list(self, user_id: str) -> list[file_dto.FileInfoDTO]:
        return await self.file_service.file_list(user_id)

    async def download(self, data: file_dto.FileDTO) -> str:
        return await self.file_service.download(data)

    async def delete(self, data: file_dto.DeleteDTO) -> None:
        await self.file_service.delete(data)

    async def delete_all(self, user_id: str) -> None:
        await self.file_service.delete_all(user_id)
