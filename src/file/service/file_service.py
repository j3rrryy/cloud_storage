from cashews import cache

from dto import request as request_dto
from dto import response as response_dto
from repository import FileRepository
from storage import FileStorage


class FileService:
    @staticmethod
    async def upload_file(data: request_dto.UploadFileRequestDTO) -> str:
        data = data.replace(size=int(data.size), path=data.path + data.name)
        await cache.delete(f"file-list:{data.user_id}")

        upload_url = await FileStorage.upload_file(data)  # type: ignore
        await FileRepository.upload_file(data)  # type: ignore
        return upload_url[upload_url.find("/", 7) :]

    @staticmethod
    async def file_info(
        data: request_dto.FileOperationRequestDTO,
    ) -> response_dto.FileInfoResponseDTO:
        if cached := await cache.get(f"file-info:{data.user_id}:{data.file_id}"):
            return cached

        info = await FileRepository.file_info(data)  # type: ignore
        info = info.replace(path=info.path[: info.path.rfind("/") + 1])
        await cache.set(f"file-info:{data.user_id}:{data.file_id}", info, 3600)
        return info

    @staticmethod
    async def file_list(user_id: str) -> tuple[response_dto.FileInfoResponseDTO, ...]:
        if cached := await cache.get(f"file-list:{user_id}"):
            return cached

        files = await FileRepository.file_list(user_id)  # type: ignore

        files = tuple(
            file.replace(path=file.path[: file.path.rfind("/") + 1]) for file in files
        )
        await cache.set(f"file-list:{user_id}", files, 3600)
        return files

    @staticmethod
    async def download_file(data: request_dto.FileOperationRequestDTO) -> str:
        info = await cache.get(f"download-file-info:{data.user_id}:{data.file_id}")

        if not info:
            info = await FileRepository.file_info(data)  # type: ignore
            await cache.set(
                f"download-file-info:{data.user_id}:{data.file_id}", info, 3600
            )

        download_url = await FileStorage.download_file(info)  # type: ignore
        return download_url[download_url.find("/", 7) :]

    @staticmethod
    async def delete_files(data: request_dto.DeleteFilesRequestDTO) -> None:
        await cache.delete(f"file-list:{data.user_id}")
        files = await FileRepository.get_file_list_to_delete(data)  # type: ignore
        await FileStorage.delete_files(files)  # type: ignore
        await FileRepository.delete_files(data)  # type: ignore

        for file_id in data.file_ids:
            await cache.delete_many(
                f"file-info:{data.user_id}:{file_id}",
                f"download-file-info:{data.user_id}:{file_id}",
            )

    @staticmethod
    async def delete_all_files(user_id: str) -> None:
        await cache.delete(f"file-list:{user_id}")
        await cache.delete_match(f"file-info:{user_id}:*")
        await cache.delete_match(f"download-file-info:{user_id}:*")
        await FileStorage.delete_all_files(user_id)  # type: ignore
        await FileRepository.delete_all_files(user_id)  # type: ignore
