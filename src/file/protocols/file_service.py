from typing import Protocol

from dto import request as request_dto
from dto import response as response_dto


class FileServiceProtocol(Protocol):
    async def initiate_upload(
        self, data: request_dto.InitiateUploadRequestDTO
    ) -> response_dto.InitiateUploadResponseDTO: ...

    async def complete_upload(
        self, data: request_dto.CompleteUploadRequestDTO
    ) -> None: ...

    async def abort_upload(self, data: request_dto.AbortUploadRequestDTO) -> None: ...

    async def file_info(
        self, data: request_dto.FileRequestDTO
    ) -> response_dto.FileInfoResponseDTO: ...

    async def file_list(
        self, user_id: str
    ) -> list[response_dto.FileInfoResponseDTO]: ...

    async def download(self, data: request_dto.FileRequestDTO) -> str: ...

    async def delete(self, data: request_dto.DeleteFilesRequestDTO) -> None: ...

    async def delete_all(self, user_id: str) -> None: ...
