from typing import AsyncIterator

from aiobotocore.client import AioBaseClient
from grpc import StatusCode

from config import Config, load_config


class CRUD:
    _BUCKET_NAME = "files"
    _config: Config = load_config()

    @classmethod
    async def upload_file(
        cls, chunk_iterator: AsyncIterator, data: dict[str, str], client: AioBaseClient
    ) -> int | None:
        OBJECT_KEY = f"{data["user_id"]}/{data["name"]}"

        try:
            await client.head_bucket(Bucket=cls._BUCKET_NAME)
        except Exception:
            await client.create_bucket(Bucket=cls._BUCKET_NAME)

        try:
            await client.head_object(Bucket=cls._BUCKET_NAME, Key=OBJECT_KEY)
            raise FileExistsError(StatusCode.ALREADY_EXISTS, "File already exists")
        except FileExistsError as exc:
            raise exc
        except Exception:
            ...

        try:
            multipart_upload = await client.create_multipart_upload(
                Bucket=cls._BUCKET_NAME, Key=OBJECT_KEY
            )
            upload_id = multipart_upload["UploadId"]

            parts = []
            part_number = 1
            total_size = 0

            async for chunk in chunk_iterator:
                part = await client.upload_part(
                    Bucket=cls._BUCKET_NAME,
                    Key=OBJECT_KEY,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=chunk.chunk,
                )
                parts.append({"PartNumber": part_number, "ETag": part["ETag"]})
                part_number += 1
                chunk_size = len(chunk.chunk)
                total_size += chunk_size

            await client.complete_multipart_upload(
                Bucket=cls._BUCKET_NAME,
                Key=OBJECT_KEY,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts},
            )
            return total_size
        except Exception as exc:
            await client.abort_multipart_upload(
                Bucket=cls._BUCKET_NAME, Key=OBJECT_KEY, UploadId=upload_id
            )
            exc.args = (StatusCode.INTERNAL, "Internal storage error")
            raise exc

    @classmethod
    async def download_file(cls, data: dict[str, str], client: AioBaseClient) -> str:
        OBJECT_KEY = f"{data["user_id"]}/{data["name"]}"

        try:
            await client.head_object(Bucket=cls._BUCKET_NAME, Key=OBJECT_KEY)
        except Exception:
            raise FileNotFoundError(StatusCode.NOT_FOUND, "File not found")

        try:
            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": cls._BUCKET_NAME, "Key": OBJECT_KEY},
                ExpiresIn=3600,
            )
            return url
        except FileNotFoundError as exc:
            raise exc
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, "Internal storage error")
            raise exc

    @classmethod
    async def delete_files(cls, data: dict[str, str], client: AioBaseClient) -> None:
        try:
            for filename in data["filenames"]:
                OBJECT_KEY = f"{data["user_id"]}/{filename}"

                try:
                    await client.head_object(Bucket=cls._BUCKET_NAME, Key=OBJECT_KEY)
                except Exception:
                    raise FileNotFoundError(StatusCode.NOT_FOUND, "File not found")

                await client.delete_object(Bucket=cls._BUCKET_NAME, Key=OBJECT_KEY)
        except FileNotFoundError as exc:
            raise exc
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, "Internal storage error")
            raise exc

    @classmethod
    async def delete_all_files(cls, user_id: str, client: AioBaseClient) -> None:
        PREFIX = f"{user_id}/"

        try:
            paginator = client.get_paginator("list_objects_v2")

            async for page in paginator.paginate(
                Bucket=cls._BUCKET_NAME, Prefix=PREFIX
            ):
                if page.get("Contents", 0):
                    delete_requests = [{"Key": obj["Key"]} for obj in page["Contents"]]

                    await client.delete_objects(
                        Bucket=cls._BUCKET_NAME, Delete={"Objects": delete_requests}
                    )
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, "Internal storage error")
            raise exc
