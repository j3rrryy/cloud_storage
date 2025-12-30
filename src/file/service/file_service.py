import asyncio

from cashews import cache
from grpc import StatusCode

from dto import request as request_dto
from dto import response as response_dto
from exceptions import (
    FileNotFoundException,
    FileTooLargeException,
    NoUploadedPartsException,
)
from repository import FileRepository
from settings import Settings
from storage import FileStorage
from utils import (
    file_all_keys,
    file_download_key,
    file_info_key,
    file_list_key,
    file_upload_key,
)


class FileService:
    @classmethod
    async def initiate_upload(
        cls, data: request_dto.InitiateUploadRequestDTO
    ) -> response_dto.InitiateUploadResponseDTO:
        if data.size > Settings.MAX_FILE_SIZE:
            raise FileTooLargeException(StatusCode.INVALID_ARGUMENT, "File too large")

        await FileRepository.check_if_name_is_taken(data)  # type: ignore
        upload = await FileStorage.initiate_upload(data)  # type: ignore

        initiated_upload = request_dto.InitiatedUploadRequestDTO(
            upload.file_id, data.user_id, data.name, data.size
        )
        await cache.set(
            file_upload_key(data.user_id, upload.upload_id), initiated_upload, 3600 * 24
        )
        return upload

    @classmethod
    async def complete_upload(cls, data: request_dto.CompleteUploadRequestDTO) -> None:
        if not data.parts:
            raise NoUploadedPartsException(
                StatusCode.INVALID_ARGUMENT, "Uploaded parts list cannot be empty"
            )

        upload_key = file_upload_key(data.user_id, data.upload_id)
        upload = await cls._get_upload(upload_key)
        await FileStorage.complete_upload(upload.file_id, data)  # type: ignore
        await FileRepository.complete_upload(upload)  # type: ignore
        await cache.delete_many(file_list_key(data.user_id), upload_key)

    @classmethod
    async def abort_upload(cls, data: request_dto.AbortUploadRequestDTO) -> None:
        upload_key = file_upload_key(data.user_id, data.upload_id)
        upload = await cls._get_upload(upload_key)
        await FileStorage.abort_upload(upload.file_id, data.upload_id)  # type: ignore
        await cache.delete(upload_key)

    @staticmethod
    async def file_info(
        data: request_dto.FileRequestDTO,
    ) -> response_dto.FileInfoResponseDTO:
        info_key = file_info_key(data.user_id, data.file_id)
        if cached := await cache.get(info_key):
            return cached

        info = await FileRepository.file_info(data)  # type: ignore
        await cache.set(info_key, info, 3600)
        return info

    @staticmethod
    async def file_list(user_id: str) -> list[response_dto.FileInfoResponseDTO]:
        list_key = file_list_key(user_id)
        if cached := await cache.get(list_key):
            return cached

        files = await FileRepository.file_list(user_id)  # type: ignore
        await cache.set(list_key, files, 3600)
        return files

    @staticmethod
    async def download(data: request_dto.FileRequestDTO) -> str:
        download_key = file_download_key(data.user_id, data.file_id)
        info = await cache.get(download_key)

        if not info:
            info = await FileRepository.file_info(data)  # type: ignore
            await cache.set(download_key, info, 3600)

        return await FileStorage.download(info)  # type: ignore

    @staticmethod
    async def delete(data: request_dto.DeleteFilesRequestDTO) -> None:
        if not data.file_ids:
            return

        await FileRepository.validate_user_files(data.user_id, data.file_ids)  # type: ignore
        asyncio.create_task(FileStorage.delete(data.file_ids))  # type: ignore
        await FileRepository.delete(data)  # type: ignore

        await cache.delete(file_list_key(data.user_id))
        for file_id in data.file_ids:
            await cache.delete_many(
                file_info_key(data.user_id, file_id),
                file_download_key(data.user_id, file_id),
            )

    @staticmethod
    async def delete_all(user_id: str) -> None:
        file_ids = await FileRepository.delete_all(user_id)  # type: ignore
        asyncio.create_task(FileStorage.delete(file_ids))  # type: ignore
        await cache.delete_match(file_all_keys(user_id))

    @staticmethod
    async def _get_upload(upload_key: str) -> request_dto.InitiatedUploadRequestDTO:
        if not (upload := await cache.get(upload_key)):
            raise FileNotFoundException(
                StatusCode.NOT_FOUND, "Uploading file not found"
            )
        return upload
