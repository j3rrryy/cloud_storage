from cashews import cache
from sqlalchemy.ext.asyncio import AsyncSession

from config import load_config
from database import CRUD, get_session


class DatabaseController:
    _config = load_config()

    @classmethod
    @get_session
    async def upload_file(
        cls,
        data: dict[str, str],
        *,
        session: AsyncSession,
    ) -> None:
        await CRUD.upload_file(data, session)
        await cache.delete(f"file_list-{data["user_id"]}")

    @classmethod
    @get_session
    async def file_info(
        cls,
        data: dict[str, str],
        *,
        session: AsyncSession,
    ) -> dict[str, str]:
        if cached := await cache.get(f"file_info-{data["user_id"]}-{data["file_id"]}"):
            return cached

        info = await CRUD.file_info(data["file_id"], session)
        del info["user_id"]
        await cache.set(f"file_info-{data["user_id"]}-{data["file_id"]}", info, 3600)
        return info

    @classmethod
    @get_session
    async def file_list(
        cls,
        user_id: str,
        *,
        session: AsyncSession,
    ) -> tuple[dict[str, str]]:
        if cached := await cache.get(f"file_list-{user_id}"):
            return cached

        files = await CRUD.file_list(user_id, session)

        for file in files:
            del file["user_id"]

        await cache.set(f"file_list-{user_id}", files, 3600)
        return files

    @classmethod
    @get_session
    async def delete_files(
        cls,
        data: dict[str, str],
        *,
        session: AsyncSession,
    ) -> dict[str, str]:
        filenames = await CRUD.delete_files(data, session)
        await cache.delete(f"file_list-{data["user_id"]}")
        for file_id in data["file_ids"]:
            await cache.delete(f"file_info-{data["user_id"]}-{file_id}")
        return filenames

    @classmethod
    @get_session
    async def delete_all_files(
        cls,
        user_id: str,
        *,
        session: AsyncSession,
    ) -> None:
        await CRUD.delete_all_files(user_id, session)
        await cache.delete(f"file_list-{user_id}")
        await cache.delete_match(f"file_info-{user_id}-*")
