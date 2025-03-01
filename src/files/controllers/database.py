from cashews import cache
from sqlalchemy.ext.asyncio import AsyncSession

from config import load_config
from database import CRUD, get_session
from dto import request as request_dto
from dto import response as response_dto


class DatabaseController:
    _config = load_config()

    @classmethod
    @get_session
    async def upload_file(
        cls, data: request_dto.UploadFileRequestDTO, *, session: AsyncSession
    ) -> None:
        data = data.replace(size=int(data.size), path=data.path + data.name)
        await CRUD.upload_file(data, session)
        await cache.delete(f"file_list-{data.user_id}")

    @classmethod
    @get_session
    async def file_info(
        cls, data: request_dto.FileOperationRequestDTO, *, session: AsyncSession
    ) -> response_dto.FileInfoResponseDTO:
        if cached := await cache.get(f"file_info-{data.user_id}-{data.file_id}"):
            return cached

        info = await CRUD.file_info(data, session)
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

        files = await CRUD.file_list(user_id, session)

        files = tuple(
            file.replace(user_id=None, path=file.path[: file.path.rfind("/") + 1])
            for file in files
        )
        await cache.set(f"file_list-{user_id}", files, 3600)
        return files

    @classmethod
    @get_session
    async def download_file(
        cls, data: request_dto.FileOperationRequestDTO, *, session: AsyncSession
    ) -> response_dto.FileInfoResponseDTO:
        if cached := await cache.get(
            f"download_file_info-{data.user_id}-{data.file_id}"
        ):
            return cached

        info = await CRUD.file_info(data, session)
        await cache.set(f"download_file_info-{data.user_id}-{data.file_id}", info, 3600)
        return info

    @classmethod
    @get_session
    async def delete_files(
        cls, data: request_dto.DeleteFilesRequestDTO, *, session: AsyncSession
    ) -> response_dto.DeleteFilesResponseDTO:
        files = await CRUD.delete_files(data, session)
        await cache.delete(f"file_list-{data.user_id}")

        for file_id in data.file_ids:
            await cache.delete(f"file_info-{data.user_id}-{file_id}")
            await cache.delete(f"download_file_info-{data.user_id}-{file_id}")

        return files

    @classmethod
    @get_session
    async def delete_all_files(cls, user_id: str, *, session: AsyncSession) -> None:
        await CRUD.delete_all_files(user_id, session)
        await cache.delete(f"file_list-{user_id}")
        await cache.delete_match(f"file_info-{user_id}-*")
        await cache.delete_match(f"download_file_info-{user_id}-*")
