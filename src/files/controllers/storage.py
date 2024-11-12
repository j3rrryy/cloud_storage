import math
from typing import AsyncIterator

from aiobotocore.client import AioBaseClient

from config import load_config
from storage import CRUD, get_client


class StorageController:
    _config = load_config()

    @classmethod
    @get_client
    async def upload_file(
        cls, data_iterator: AsyncIterator, client: AioBaseClient
    ) -> dict[str, str]:
        SIZE_NAMES = ("B", "KB", "MB", "GB")

        metadata = await anext(data_iterator)
        data = {"user_id": metadata.user_id, "name": metadata.name}

        file_size = await CRUD.upload_file(data_iterator, data, client)

        i = int(math.floor(math.log(file_size, 1024)))
        converted_size = round(file_size / 1024**i, 2)
        data["size"] = f"{converted_size} {SIZE_NAMES[i]}"
        return data

    @classmethod
    @get_client
    async def download_file(cls, data: dict[str, str], client: AioBaseClient) -> str:
        file_url = await CRUD.download_file(data, client)
        relative_url = file_url[file_url.find("/", 7) :]
        return relative_url

    @classmethod
    @get_client
    async def delete_files(cls, data: dict[str, str], client: AioBaseClient) -> None:
        await CRUD.delete_files(data, client)

    @classmethod
    @get_client
    async def delete_all_files(cls, user_id: str, client: AioBaseClient) -> None:
        await CRUD.delete_all_files(user_id, client)
