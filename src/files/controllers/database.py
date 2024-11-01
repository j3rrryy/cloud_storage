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

        info = await CRUD.file_info(data, session)
        info["uploaded"] = info["uploaded"].strftime("%d.%m.%Y")
        del info["path"], info["user_id"]
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
            file["uploaded"] = file["uploaded"].strftime("%d.%m.%Y")
            del file["path"], file["user_id"]

        await cache.set(f"file_list-{user_id}", files, 3600)
        return files

    @classmethod
    @get_session
    async def download_file(
        cls,
        data: dict[str, str],
        *,
        session: AsyncSession,
    ) -> str:
        if cached := await cache.get(f"download_file-{data["user_id"]}-{data["file_id"]}"):
            return cached

        info = await CRUD.file_info(data, session)
        await cache.set(f"download_file-{data["user_id"]}-{data["file_id"]}", info["path"], 3600)
        return info["path"]

    @classmethod
    @get_session
    async def delete_files(
        cls,
        data: dict[str, str],
        *,
        session: AsyncSession,
    ) -> tuple[str]:
        paths = await CRUD.delete_files(data, session)
        await cache.delete(f"file_list-{data["user_id"]}")
        return paths

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
