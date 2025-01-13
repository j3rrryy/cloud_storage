from aiobotocore.client import AioBaseClient
from grpc import StatusCode

from config import load_config


class CRUD:
    _config = load_config()
    _BUCKET_NAME = _config.minio.bucket

    @classmethod
    async def create_bucket(cls, client: AioBaseClient) -> None:
        try:
            await client.head_bucket(Bucket=cls._BUCKET_NAME)
        except Exception:
            await client.create_bucket(Bucket=cls._BUCKET_NAME)

    @classmethod
    async def upload_file(
        cls, data: dict[str, str | int], client: AioBaseClient
    ) -> str:
        try:
            url = await client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": cls._BUCKET_NAME,
                    "Key": f"{data['user_id']}{data['path']}",
                },
                ExpiresIn=15,
            )
            return url
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, "Internal storage error")
            raise exc

    @classmethod
    async def download_file(
        cls, data: dict[str, str | int], client: AioBaseClient
    ) -> str:
        OBJECT_KEY = f"{data['user_id']}{data['path']}"

        try:
            await client.head_object(Bucket=cls._BUCKET_NAME, Key=OBJECT_KEY)
        except Exception:
            raise FileNotFoundError(StatusCode.NOT_FOUND, "File not found")

        try:
            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": cls._BUCKET_NAME, "Key": OBJECT_KEY},
                ExpiresIn=15,
            )
            return url
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, "Internal storage error")
            raise exc

    @classmethod
    async def delete_files(cls, data: dict[str, str], client: AioBaseClient) -> None:
        try:
            for path in data["files"]:
                await client.delete_object(
                    Bucket=cls._BUCKET_NAME, Key=f"{data['user_id']}{path}"
                )
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, "Internal storage error")
            raise exc

    @classmethod
    async def delete_all_files(cls, user_id: str, client: AioBaseClient) -> None:
        try:
            paginator = client.get_paginator("list_objects_v2")

            async for page in paginator.paginate(
                Bucket=cls._BUCKET_NAME,
                Prefix=f"{user_id}/",
            ):
                if page.get("Contents", 0):
                    delete_requests = [{"Key": obj["Key"]} for obj in page["Contents"]]

                    await client.delete_objects(
                        Bucket=cls._BUCKET_NAME,
                        Delete={"Objects": delete_requests},
                    )
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, "Internal storage error")
            raise exc
