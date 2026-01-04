from datetime import datetime
from unittest.mock import AsyncMock

from cashews import Cache
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from types_aiobotocore_s3 import S3Client

from dto import response as response_dto
from repository import File, FileRepository
from storage import FileStorage

USER_ID = "00e51a90-0f94-4ecb-8dd1-399ba409508e"
UPLOAD_ID = "YjUzZjE5MzktY2U2Zi00NmNiLWE3Y2ItNmUwY2M2ODE3NDA5LjBmNzcyN2I0LTNkZjgtNGQ0ZS1hNTc3LTRiMmRjOTFjOTc2ZXgxNzYyOTAwNTgxNzg3NDgwOTI5"
URL = "http://minio:9000/s3-files/662c3e99-65dc-4a26-a2c2-bbd9f4e1fac4/test_file?AWSAccessKeyId=test_username&Signature=kn3PpoJ%2BwQBYVmpYl%2B8cZK2KM0s%3D&Expires=1741791573"
RELATIVE_URL = "/s3-files/662c3e99-65dc-4a26-a2c2-bbd9f4e1fac4/test_file?AWSAccessKeyId=test_username&Signature=kn3PpoJ%2BwQBYVmpYl%2B8cZK2KM0s%3D&Expires=1741791573"
ETAG = "fac024381d213f9949facd263b44aea4"
FILE_ID = "b8a47c8d-9203-456a-aa58-ceab64b13cbb"
SIZE = 123
NAME = "test_name"
TIMESTAMP = datetime.fromisoformat("1970-01-01T00:02:03Z")


def create_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return AsyncMock(spec=async_sessionmaker[AsyncSession])


def create_client() -> S3Client:
    client = AsyncMock(spec=S3Client)
    client.create_multipart_upload = AsyncMock(return_value={"UploadId": UPLOAD_ID})
    client.generate_presigned_url = AsyncMock(return_value=URL)
    return client


def create_cache() -> Cache:
    return AsyncMock(spec=Cache)


def create_file_repository() -> FileRepository:
    crud = AsyncMock(spec=FileRepository)
    crud.file_info = AsyncMock(
        return_value=response_dto.FileInfoResponseDTO(
            FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP
        )
    )
    crud.file_list = AsyncMock(
        return_value=(
            response_dto.FileInfoResponseDTO(FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP),
        )
    )
    return crud


def create_file_storage() -> FileStorage:
    crud = AsyncMock(spec=FileStorage)
    crud.initiate_upload = AsyncMock(
        return_value=response_dto.InitiateUploadResponseDTO(
            FILE_ID,
            UPLOAD_ID,
            SIZE,
            [response_dto.UploadPartResponseDTO(1, RELATIVE_URL)],
        )
    )
    crud.download = AsyncMock(return_value=RELATIVE_URL)
    return crud


def create_file() -> File:
    return File(
        file_id=FILE_ID, user_id=USER_ID, name=NAME, size=SIZE, uploaded_at=TIMESTAMP
    )
