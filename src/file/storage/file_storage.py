import os

from grpc import StatusCode
from types_aiobotocore_s3 import S3Client

from dto import request as request_dto
from dto import response as response_dto
from utils import with_storage


class FileStorage:
    BUCKET_NAME = os.environ["MINIO_FILE_BUCKET"]

    @classmethod
    @with_storage
    async def upload_file(
        cls, data: request_dto.UploadFileRequestDTO, client: S3Client
    ) -> str:
        url = await client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": cls.BUCKET_NAME,
                "Key": f"{data.user_id}{data.path}",
            },
            ExpiresIn=30,
        )
        return url

    @classmethod
    @with_storage
    async def download_file(
        cls, data: response_dto.FileInfoResponseDTO, client: S3Client
    ) -> str:
        OBJECT_KEY = f"{data.user_id}{data.path}"

        try:
            await client.head_object(Bucket=cls.BUCKET_NAME, Key=OBJECT_KEY)
        except Exception:
            raise FileNotFoundError(StatusCode.NOT_FOUND, "File not found")

        url = await client.generate_presigned_url(
            "get_object",
            Params={"Bucket": cls.BUCKET_NAME, "Key": OBJECT_KEY},
            ExpiresIn=30,
        )
        return url

    @classmethod
    @with_storage
    async def delete_files(
        cls, data: response_dto.DeleteFilesResponseDTO, client: S3Client
    ) -> None:
        for path in data.paths:
            await client.delete_object(
                Bucket=cls.BUCKET_NAME, Key=f"{data.user_id}{path}"
            )

    @classmethod
    @with_storage
    async def delete_all_files(cls, user_id: str, client: S3Client) -> None:
        paginator = client.get_paginator("list_objects_v2")

        async for page in paginator.paginate(
            Bucket=cls.BUCKET_NAME, Prefix=f"{user_id}/"
        ):
            if page.get("Contents", 0):
                delete_requests = [{"Key": obj["Key"]} for obj in page["Contents"]]  # type: ignore

                await client.delete_objects(
                    Bucket=cls.BUCKET_NAME,
                    Delete={"Objects": delete_requests},  # type: ignore
                )
