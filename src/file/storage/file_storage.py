import asyncio
import math
import os
from uuid import uuid4

import picologging as logging
from botocore.exceptions import ClientError
from grpc import StatusCode
from types_aiobotocore_s3 import S3Client

from dto import request as request_dto
from dto import response as response_dto
from exceptions import FileNotFoundException
from utils import with_storage


class FileStorage:
    BUCKET_NAME = os.environ["MINIO_S3_BUCKET"]
    UPLOAD_CHUNK_SIZE = int(os.environ["UPLOAD_CHUNK_SIZE"])

    logger = logging.getLogger()

    @classmethod
    @with_storage
    async def initiate_upload(
        cls, data: request_dto.InitiateUploadRequestDTO, client: S3Client
    ) -> response_dto.InitiateUploadResponseDTO:
        semaphore = asyncio.Semaphore(25)

        file_id = str(uuid4())
        upload = await client.create_multipart_upload(
            Bucket=cls.BUCKET_NAME, Key=file_id
        )

        part_count = math.ceil(data.size / cls.UPLOAD_CHUNK_SIZE)
        part_size = min(data.size, cls.UPLOAD_CHUNK_SIZE)
        parts = []

        async def gen_url(part_number: int):
            async with semaphore:
                return response_dto.UploadPartResponseDTO(
                    part_number,
                    await client.generate_presigned_url(
                        "upload_part",
                        Params={
                            "Bucket": cls.BUCKET_NAME,
                            "Key": file_id,
                            "UploadId": upload["UploadId"],
                            "PartNumber": part_number,
                        },
                        ExpiresIn=3600 * 24,
                    ),
                )

        parts = await asyncio.gather(*(gen_url(i) for i in range(1, part_count + 1)))
        return response_dto.InitiateUploadResponseDTO(
            file_id=file_id,
            upload_id=upload["UploadId"],
            part_size=part_size,
            parts=parts,
        )

    @classmethod
    @with_storage
    async def complete_upload(
        cls, file_id: str, data: request_dto.CompleteUploadRequestDTO, client: S3Client
    ) -> None:
        parts = sorted(
            [
                {"PartNumber": part.part_number, "ETag": part.etag}
                for part in data.parts
            ],
            key=lambda x: x["PartNumber"],
        )
        try:
            await client.complete_multipart_upload(
                Bucket=cls.BUCKET_NAME,
                Key=file_id,
                UploadId=data.upload_id,
                MultipartUpload={"Parts": parts},  # type: ignore
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] in {"NoSuchKey", "404"}:  # type: ignore
                raise FileNotFoundException(
                    StatusCode.NOT_FOUND, "Uploading file not found"
                )
            raise

    @classmethod
    @with_storage
    async def abort_upload(cls, file_id: str, upload_id: str, client: S3Client) -> None:
        try:
            await client.abort_multipart_upload(
                Bucket=cls.BUCKET_NAME,
                Key=file_id,
                UploadId=upload_id,
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] in {"NoSuchKey", "404"}:  # type: ignore
                raise FileNotFoundException(
                    StatusCode.NOT_FOUND, "Uploading file not found"
                )
            raise

    @classmethod
    @with_storage
    async def download(
        cls, data: response_dto.FileInfoResponseDTO, client: S3Client
    ) -> str:
        try:
            await client.head_object(Bucket=cls.BUCKET_NAME, Key=data.file_id)
        except ClientError as exc:
            if exc.response["Error"]["Code"] in {"NoSuchKey", "404"}:  # type: ignore
                raise FileNotFoundException(StatusCode.NOT_FOUND, "File not found")
            raise

        url = await client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": cls.BUCKET_NAME,
                "Key": data.file_id,
                "ResponseContentDisposition": f'attachment; filename="{data.name}"',
            },
            ExpiresIn=60,
        )
        return url

    @classmethod
    @with_storage
    async def delete(cls, file_ids: tuple[str, ...], client: S3Client) -> None:
        semaphore = asyncio.Semaphore(5)
        keys = [{"Key": file_id} for file_id in file_ids]
        tasks = []

        for i in range(0, len(keys), 1000):
            chunk = keys[i : i + 1000]
            task = asyncio.create_task(cls._delete_chunk(chunk, semaphore, client))
            tasks.append(task)

        await cls._gather_tasks(tasks)

    @classmethod
    @with_storage
    async def delete_all(cls, user_id: str, client: S3Client) -> None:
        semaphore = asyncio.Semaphore(5)
        paginator = client.get_paginator("list_objects_v2")
        tasks = []

        async for page in paginator.paginate(
            Bucket=cls.BUCKET_NAME,
            Prefix=f"{user_id}/",
            PaginationConfig={"PageSize": 1000},
        ):
            if keys := page.get("Contents", []):
                chunk = [{"Key": obj["Key"]} for obj in keys]  # type: ignore
                task = asyncio.create_task(cls._delete_chunk(chunk, semaphore, client))
                tasks.append(task)

        await cls._gather_tasks(tasks)

    @classmethod
    async def _delete_chunk(
        cls, chunk: list[dict[str, str]], semaphore: asyncio.Semaphore, client: S3Client
    ):
        async with semaphore:
            await client.delete_objects(
                Bucket=cls.BUCKET_NAME,
                Delete={"Objects": chunk},  # type: ignore
            )

    @classmethod
    async def _gather_tasks(cls, tasks: list[asyncio.Task]):
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                cls.logger.error(str(r))
