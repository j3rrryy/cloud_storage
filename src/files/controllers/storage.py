from types_aiobotocore_s3 import S3Client

from config import load_config
from storage import CRUD, get_client


class StorageController:
    _config = load_config()

    @classmethod
    @get_client
    async def upload_file(cls, data: dict[str, str | int], client: S3Client) -> str:
        upload_url = await CRUD.upload_file(data, client)
        relative_url = upload_url[upload_url.find("/", 7) :]
        return relative_url

    @classmethod
    @get_client
    async def download_file(cls, data: dict[str, str | int], client: S3Client) -> str:
        data["path"] += data["name"]
        file_url = await CRUD.download_file(data, client)
        relative_url = file_url[file_url.find("/", 7) :]
        return relative_url

    @classmethod
    @get_client
    async def delete_files(cls, data: dict[str, str], client: S3Client) -> None:
        await CRUD.delete_files(data, client)

    @classmethod
    @get_client
    async def delete_all_files(cls, user_id: str, client: S3Client) -> None:
        await CRUD.delete_all_files(user_id, client)
