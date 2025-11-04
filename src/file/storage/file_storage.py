import asyncio
import os

from botocore.exceptions import ClientError
from grpc import StatusCode
from types_aiobotocore_s3 import S3Client

from dto import request as request_dto
from dto import response as response_dto
from exceptions import FileNotFoundException
from utils import with_storage


class FileStorage:
    BUCKET_NAME = os.environ["MINIO_S3_BUCKET"]

    @classmethod
    @with_storage
    async def upload_file(
        cls, data: request_dto.UploadFileRequestDTO, client: S3Client
    ) -> str:
        url = await client.generate_presigned_url(
            "put_object",
            Params={"Bucket": cls.BUCKET_NAME, "Key": f"{data.user_id}{data.path}"},
            ExpiresIn=60,
        )
        return url

    @classmethod
    @with_storage
    async def download_file(
        cls, data: response_dto.FileInfoResponseDTO, client: S3Client
    ) -> str:
        key = f"{data.user_id}{data.path}"

        try:
            await client.head_object(Bucket=cls.BUCKET_NAME, Key=key)
        except ClientError as exc:
            if exc.response["Error"]["Code"] in {"NoSuchKey", "404"}:  # type: ignore
                raise FileNotFoundException(StatusCode.NOT_FOUND, "File not found")
            raise

        url = await client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": cls.BUCKET_NAME,
                "Key": key,
                "ResponseContentDisposition": f'attachment; filename="{data.name}"',
            },
            ExpiresIn=60,
        )
        return url

    @classmethod
    @with_storage
    async def delete_files(
        cls, data: response_dto.DeleteFilesResponseDTO, client: S3Client
    ) -> None:
        keys = [{"Key": f"{data.user_id}{path}"} for path in data.paths]
        tasks = []

        for i in range(0, len(keys), 1000):
            chunk = keys[i : i + 1000]
            task = asyncio.create_task(cls._delete_chunk(chunk, client))
            tasks.append(task)

        await cls._raise_on_exceptions(tasks)

    @classmethod
    @with_storage
    async def delete_all_files(cls, user_id: str, client: S3Client) -> None:
        paginator = client.get_paginator("list_objects_v2")
        tasks = []

        async for page in paginator.paginate(
            Bucket=cls.BUCKET_NAME,
            Prefix=f"{user_id}/",
            PaginationConfig={"PageSize": 1000},
        ):
            if keys := page.get("Contents", []):
                chunk = [{"Key": obj["Key"]} for obj in keys]  # type: ignore
                task = asyncio.create_task(cls._delete_chunk(chunk, client))
                tasks.append(task)

        await cls._raise_on_exceptions(tasks)

    @classmethod
    async def _delete_chunk(cls, chunk: list[dict[str, str]], client: S3Client):
        await client.delete_objects(
            Bucket=cls.BUCKET_NAME,
            Delete={"Objects": chunk},  # type: ignore
        )

    @staticmethod
    async def _raise_on_exceptions(tasks: list[asyncio.Task]):
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                raise r
