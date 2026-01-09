from types_aiobotocore_s3 import S3Client

from protocols import S3ClientProtocol
from settings import Settings
from utils import storage_exception_handler


class MinIOAdapter(S3ClientProtocol):
    def __init__(self, client: S3Client):
        self._client = client

    @storage_exception_handler
    async def create_multipart_upload(self, file_id: str) -> str:
        upload = await self._client.create_multipart_upload(
            Bucket=Settings.MINIO_S3_BUCKET, Key=file_id
        )
        return upload["UploadId"]

    @storage_exception_handler
    async def generate_upload_presigned_url(
        self, file_id: str, upload_id: str, part_number: int
    ) -> str:
        return await self._client.generate_presigned_url(
            "upload_part",
            Params={
                "Bucket": Settings.MINIO_S3_BUCKET,
                "Key": file_id,
                "UploadId": upload_id,
                "PartNumber": part_number,
            },
            ExpiresIn=Settings.UPLOAD_PRESIGNED_URL_EXPIRATION_TIME,
        )

    @storage_exception_handler
    async def complete_multipart_upload(
        self, file_id: str, upload_id: str, parts: list[dict[str, int | str]]
    ) -> None:
        await self._client.complete_multipart_upload(
            Bucket=Settings.MINIO_S3_BUCKET,
            Key=file_id,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts},  # type: ignore
        )

    @storage_exception_handler
    async def abort_multipart_upload(self, file_id: str, upload_id: str) -> None:
        await self._client.abort_multipart_upload(
            Bucket=Settings.MINIO_S3_BUCKET, Key=file_id, UploadId=upload_id
        )

    @storage_exception_handler
    async def generate_download_presigned_url(
        self, file_id: str, file_name: str
    ) -> str:
        return await self._client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": Settings.MINIO_S3_BUCKET,
                "Key": file_id,
                "ResponseContentDisposition": f'attachment; filename="{file_name}"',
            },
            ExpiresIn=Settings.DOWNLOAD_PRESIGNED_URL_EXPIRATION_TIME,
        )

    @storage_exception_handler
    async def delete_objects(self, objects: list[dict[str, str]]) -> None:
        await self._client.delete_objects(
            Bucket=Settings.MINIO_S3_BUCKET,
            Delete={"Objects": objects},  # type: ignore
        )

    async def ping(self) -> None:
        await self._client.list_buckets()
