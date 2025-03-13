from cashews import cache
from sqlalchemy.ext.asyncio import AsyncSession
from types_aiobotocore_s3 import S3Client

from dto import request as request_dto
from dto import response as response_dto
from repository import FileRepository, get_session
from storage import FileStorage, get_client


class FileService:
    @classmethod
    @get_client
    @get_session
    async def upload_file(
        cls,
        data: request_dto.UploadFileRequestDTO,
        *,
        session: AsyncSession,
        client: S3Client,
    ) -> str:
        data = data.replace(size=int(data.size), path=data.path + data.name)
        await FileRepository.upload_file(data, session)
        await cache.delete(f"file_list-{data.user_id}")

        upload_url = await FileStorage.upload_file(data, client)
        relative_url = upload_url[upload_url.find("/", 7) :]
        return relative_url

    @classmethod
    @get_session
    async def file_info(
        cls, data: request_dto.FileOperationRequestDTO, *, session: AsyncSession
    ) -> response_dto.FileInfoResponseDTO:
        if cached := await cache.get(f"file_info-{data.user_id}-{data.file_id}"):
            return cached

        info = await FileRepository.file_info(data, session)
        info = info.replace(user_id=None, path=info.path[: info.path.rfind("/") + 1])
        await cache.set(f"file_info-{data.user_id}-{data.file_id}", info, 3600)
        return info

    @classmethod
    @get_session
    async def file_list(
        cls, user_id: str, *, session: AsyncSession
    ) -> tuple[response_dto.FileInfoResponseDTO, ...]:
        if cached := await cache.get(f"file_list-{user_id}"):
            return cached

        files = await FileRepository.file_list(user_id, session)

        files = tuple(
            file.replace(user_id=None, path=file.path[: file.path.rfind("/") + 1])
            for file in files
        )
        await cache.set(f"file_list-{user_id}", files, 3600)
        return files

    @classmethod
    @get_client
    @get_session
    async def download_file(
        cls,
        data: request_dto.FileOperationRequestDTO,
        *,
        session: AsyncSession,
        client: S3Client,
    ) -> str:
        info = await cache.get(f"download_file_info-{data.user_id}-{data.file_id}")

        if not info:
            info = await FileRepository.file_info(data, session)
            await cache.set(
                f"download_file_info-{data.user_id}-{data.file_id}", info, 3600
            )

        download_url = await FileStorage.download_file(info, client)
        relative_url = download_url[download_url.find("/", 7) :]
        return relative_url

    @classmethod
    @get_client
    @get_session
    async def delete_files(
        cls,
        data: request_dto.DeleteFilesRequestDTO,
        *,
        session: AsyncSession,
        client: S3Client,
    ) -> None:
        files = await FileRepository.delete_files(data, session)
        await FileStorage.delete_files(files, client)
        await cache.delete(f"file_list-{data.user_id}")

        for file_id in data.file_ids:
            await cache.delete_many(
                f"file_info-{data.user_id}-{file_id}",
                f"download_file_info-{data.user_id}-{file_id}",
            )

    @classmethod
    @get_client
    @get_session
    async def delete_all_files(
        cls, user_id: str, *, session: AsyncSession, client: S3Client
    ) -> None:
        await FileRepository.delete_all_files(user_id, session)
        await FileStorage.delete_all_files(user_id, client)
        await cache.delete(f"file_list-{user_id}")
        await cache.delete_match(f"file_info-{user_id}-*")
        await cache.delete_match(f"download_file_info-{user_id}-*")
