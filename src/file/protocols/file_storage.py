from typing import Protocol

from dto import request as request_dto
from dto import response as response_dto


class FileStorageProtocol(Protocol):
    async def initiate_upload(
        self, data: request_dto.InitiateUploadRequestDTO
    ) -> response_dto.InitiateUploadResponseDTO: ...

    async def complete_upload(
        self, file_id: str, data: request_dto.CompleteUploadRequestDTO
    ) -> None: ...

    async def abort_upload(self, file_id: str, upload_id: str) -> None: ...

    async def download(self, data: response_dto.FileInfoResponseDTO) -> str: ...

    async def delete(self, file_ids: list[str]) -> None: ...

    async def ping(self) -> None: ...
