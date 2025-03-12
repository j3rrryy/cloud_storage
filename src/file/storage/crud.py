from grpc import StatusCode
from types_aiobotocore_s3 import S3Client

from config import load_config
from dto import request as request_dto
from dto import response as response_dto


class CRUD:
    _config = load_config()
    _BUCKET_NAME = _config.minio.bucket

    @classmethod
    async def upload_file(
        cls, data: request_dto.UploadFileRequestDTO, client: S3Client
    ) -> str:
        try:
            url = await client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": cls._BUCKET_NAME,
                    "Key": f"{data.user_id}{data.path}",
                },
                ExpiresIn=30,
            )
            return url
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, f"Internal storage error, {exc}")
            raise exc

    @classmethod
    async def download_file(
        cls, data: response_dto.FileInfoResponseDTO, client: S3Client
    ) -> str:
        OBJECT_KEY = f"{data.user_id}{data.path}"

        try:
            await client.head_object(Bucket=cls._BUCKET_NAME, Key=OBJECT_KEY)
        except Exception:
            raise FileNotFoundError(StatusCode.NOT_FOUND, "File not found")

        try:
            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": cls._BUCKET_NAME, "Key": OBJECT_KEY},
                ExpiresIn=30,
            )
            return url
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, f"Internal storage error, {exc}")
            raise exc

    @classmethod
    async def delete_files(
        cls, data: response_dto.DeleteFilesResponseDTO, client: S3Client
    ) -> None:
        try:
            for path in data.paths:
                await client.delete_object(
                    Bucket=cls._BUCKET_NAME, Key=f"{data.user_id}{path}"
                )
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, f"Internal storage error, {exc}")
            raise exc

    @classmethod
    async def delete_all_files(cls, user_id: str, client: S3Client) -> None:
        try:
            paginator = client.get_paginator("list_objects_v2")

            async for page in paginator.paginate(
                Bucket=cls._BUCKET_NAME, Prefix=f"{user_id}/"
            ):
                if page.get("Contents", 0):
                    delete_requests = [{"Key": obj["Key"]} for obj in page["Contents"]]

                    await client.delete_objects(
                        Bucket=cls._BUCKET_NAME,
                        Delete={"Objects": delete_requests},  # type: ignore
                    )
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, f"Internal storage error, {exc}")
            raise exc
