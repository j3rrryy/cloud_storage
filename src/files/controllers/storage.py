from types_aiobotocore_s3 import S3Client

from config import load_config
from dto import request as request_dto
from dto import response as response_dto
from storage import CRUD, get_client


class StorageController:
    _config = load_config()

    @classmethod
    @get_client
    async def upload_file(
        cls, data: request_dto.UploadFileRequestDTO, client: S3Client
    ) -> str:
        upload_url = await CRUD.upload_file(data, client)
        relative_url = upload_url[upload_url.find("/", 7) :]
        return relative_url

    @classmethod
    @get_client
    async def download_file(
        cls, data: response_dto.FileInfoResponseDTO, client: S3Client
    ) -> str:
        download_url = await CRUD.download_file(data, client)
        relative_url = download_url[download_url.find("/", 7) :]
        return relative_url

    @classmethod
    @get_client
    async def delete_files(
        cls, data: response_dto.DeleteFilesResponseDTO, client: S3Client
    ) -> None:
        await CRUD.delete_files(data, client)

    @classmethod
    @get_client
    async def delete_all_files(cls, user_id: str, client: S3Client) -> None:
        await CRUD.delete_all_files(user_id, client)
