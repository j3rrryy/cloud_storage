from aiobotocore.client import AioBaseClient

from config import load_config
from storage import CRUD, get_client


class StorageController:
    _config = load_config()

    @classmethod
    @get_client
    async def create_bucket(cls, client: AioBaseClient) -> None:
        await CRUD.create_bucket(client)

    @classmethod
    @get_client
    async def upload_file(
        cls, data: dict[str, str | int], client: AioBaseClient
    ) -> str:
        upload_url = await CRUD.upload_file(data, client)
        relative_url = upload_url[upload_url.find("/", 7) :]
        return relative_url

    @classmethod
    @get_client
    async def download_file(
        cls, data: dict[str, str | int], client: AioBaseClient
    ) -> str:
        data["path"] += data["name"]
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
