from typing import Protocol

from dto import request as request_dto
from dto import response as response_dto


class FileRepositoryProtocol(Protocol):
    async def check_if_name_is_taken(
        self, data: request_dto.InitiateUploadRequestDTO
    ) -> None: ...

    async def complete_upload(
        self, data: request_dto.InitiatedUploadRequestDTO
    ) -> None: ...

    async def file_info(
        self, data: request_dto.FileRequestDTO
    ) -> response_dto.FileInfoResponseDTO: ...

    async def file_list(
        self, user_id: str
    ) -> list[response_dto.FileInfoResponseDTO]: ...

    async def delete(self, data: request_dto.DeleteFilesRequestDTO) -> None: ...

    async def delete_all(self, user_id: str) -> list[str]: ...
