import math
from typing import AsyncGenerator, AsyncIterator

from config import load_config
from storage import CRUD


class StorageController:
    _config = load_config()

    @classmethod
    async def upload_file(
        cls,
        data_iterator: AsyncIterator,
    ) -> dict[str, str]:
        SIZE_NAMES = ("B", "KB", "MB", "GB")

        metadata = await anext(data_iterator)
        data = {"user_id": metadata.user_id, "name": metadata.name}
        data["user_dir"] = f"files/{data["user_id"]}/"
        data["path"] = data["user_dir"] + data["name"]

        file_size = await CRUD.upload_file(data_iterator, data)

        i = int(math.floor(math.log(file_size, 1024)))
        converted_size = round(file_size / 1024 ** i, 2)
        data["size"] = f"{converted_size} {SIZE_NAMES[i]}"
        del data["user_dir"]

        return data

    @classmethod
    async def download_file(
        cls,
        file_path: str,
    ) -> AsyncGenerator[bytes, None]:
        chunk_generator = CRUD.download_file(file_path)
        return chunk_generator

    @classmethod
    async def delete_files(cls, file_paths: tuple[str]) -> None:
        await CRUD.delete_files(file_paths)

    @classmethod
    async def delete_all_files(cls, user_id: str) -> None:
        await CRUD.delete_all_files(user_id)
