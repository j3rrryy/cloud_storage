import asyncio
from typing import Any

from cashews import Cache

from dto import request as request_dto
from dto import response as response_dto
from exceptions import FileNotFoundException, FileTooLargeException
from protocols import FileRepositoryProtocol, FileServiceProtocol, FileStorageProtocol
from settings import Settings
from utils import file_list_key, file_name_key, file_upload_key


class FileService(FileServiceProtocol):
    def __init__(
        self,
        file_repository: FileRepositoryProtocol,
        file_storage: FileStorageProtocol,
        cache: Cache,
    ):
        self._file_repository = file_repository
        self._file_storage = file_storage
        self._cache = cache

    async def initiate_upload(
        self, data: request_dto.InitiateUploadRequestDTO
    ) -> response_dto.InitiateUploadResponseDTO:
        if data.size > Settings.MAX_FILE_SIZE:
            raise FileTooLargeException

        await self._file_repository.check_if_name_is_taken(data)
        upload = await self._file_storage.initiate_upload(data)

        initiated_upload = request_dto.InitiatedUploadRequestDTO(
            upload.file_id, data.user_id, data.name, data.size
        )
        upload_key = file_upload_key(data.user_id, upload.upload_id)
        await self._cache.set(upload_key, initiated_upload, 24 * 3600)
        return upload

    async def complete_upload(self, data: request_dto.CompleteUploadRequestDTO) -> None:
        upload_key = file_upload_key(data.user_id, data.upload_id)
        upload = await self._get_upload(upload_key)
        await self._file_storage.complete_upload(upload.file_id, data)
        await self._file_repository.complete_upload(upload)
        await self._cache.delete_many(file_list_key(data.user_id), upload_key)

    async def abort_upload(self, data: request_dto.AbortUploadRequestDTO) -> None:
        upload_key = file_upload_key(data.user_id, data.upload_id)
        upload = await self._get_upload(upload_key)
        await self._file_storage.abort_upload(upload.file_id, data.upload_id)
        await self._cache.delete(upload_key)

    async def file_list(self, user_id: str) -> list[response_dto.FileInfoResponseDTO]:
        list_key = file_list_key(user_id)
        files = await self._get_cached(
            list_key, self._file_repository.file_list, user_id
        )
        return files

    async def download(self, data: request_dto.FileRequestDTO) -> str:
        name_key = file_name_key(data.user_id, data.file_id)
        name = await self._get_cached(
            name_key, self._file_repository.file_name, data.user_id, data.file_id
        )
        return await self._file_storage.download(data.file_id, name)

    async def delete(self, data: request_dto.DeleteFilesRequestDTO) -> None:
        if not data.file_ids:
            return
        await self._file_repository.delete(data)
        asyncio.create_task(self._file_storage.delete(data.file_ids))
        await self._invalidate_cache(data.user_id, data.file_ids)

    async def delete_all(self, user_id: str) -> None:
        file_ids = await self._file_repository.delete_all(user_id)
        asyncio.create_task(self._file_storage.delete(file_ids))
        await self._invalidate_cache(user_id, file_ids)

    async def _get_upload(
        self, upload_key: str
    ) -> request_dto.InitiatedUploadRequestDTO:
        if not (upload := await self._cache.get(upload_key)):
            raise FileNotFoundException
        return upload

    async def _get_cached(
        self, key: str, getter, *args, ttl: int = 3600, **kwargs
    ) -> Any:
        if cached := await self._cache.get(key):
            return cached
        value = await getter(*args, **kwargs)
        await self._cache.set(key, value, ttl)
        return value

    async def _invalidate_cache(self, user_id: str, file_ids: list[str]):
        await self._cache.delete(file_list_key(user_id))
        if file_ids:
            keys = (file_name_key(user_id, file_id) for file_id in file_ids)
            await self._cache.delete_many(*keys)
