import asyncio

from cashews import cache

from dto import request as request_dto
from dto import response as response_dto
from repository import FileRepository
from storage import FileStorage
from utils import file_all_keys, file_download_key, file_info_key, file_list_key


class FileService:
    @staticmethod
    async def upload_file(data: request_dto.UploadFileRequestDTO) -> str:
        data = data.replace(size=int(data.size))
        await cache.delete(file_list_key(data.user_id))

        file_id = await FileRepository.upload_file(data)  # type: ignore
        upload_url = await FileStorage.upload_file(file_id)  # type: ignore
        return upload_url[upload_url.find("/", 7) :]

    @staticmethod
    async def file_info(
        data: request_dto.FileOperationRequestDTO,
    ) -> response_dto.FileInfoResponseDTO:
        info_key = file_info_key(data.user_id, data.file_id)
        if cached := await cache.get(info_key):
            return cached

        info = await FileRepository.file_info(data)  # type: ignore
        await cache.set(info_key, info, 3600)
        return info

    @staticmethod
    async def file_list(user_id: str) -> tuple[response_dto.FileInfoResponseDTO, ...]:
        list_key = file_list_key(user_id)
        if cached := await cache.get(list_key):
            return cached

        files = await FileRepository.file_list(user_id)  # type: ignore
        await cache.set(list_key, files, 3600)
        return files

    @staticmethod
    async def download_file(data: request_dto.FileOperationRequestDTO) -> str:
        download_key = file_download_key(data.user_id, data.file_id)
        info = await cache.get(download_key)

        if not info:
            info = await FileRepository.file_info(data)  # type: ignore
            await cache.set(download_key, info, 3600)

        download_url = await FileStorage.download_file(info)  # type: ignore
        return download_url[download_url.find("/", 7) :]

    @staticmethod
    async def delete_files(data: request_dto.DeleteFilesRequestDTO) -> None:
        if not data.file_ids:
            return

        await cache.delete(file_list_key(data.user_id))
        await FileRepository.validate_user_files(data.user_id, data.file_ids)  # type: ignore
        await FileStorage.delete_files(data.file_ids)  # type: ignore
        await FileRepository.delete_files(data)  # type: ignore

        for file_id in data.file_ids:
            await cache.delete_many(
                file_info_key(data.user_id, file_id),
                file_download_key(data.user_id, file_id),
            )

    @staticmethod
    async def delete_all_files(user_id: str) -> None:
        await cache.delete_match(file_all_keys(user_id))
        asyncio.create_task(FileStorage.delete_all_files(user_id))  # type: ignore
        await FileRepository.delete_all_files(user_id)  # type: ignore
