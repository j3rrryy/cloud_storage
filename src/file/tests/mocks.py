from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from dto import response as response_dto

USER_ID = "00e51a90-0f94-4ecb-8dd1-399ba409508e"
UPLOAD_ID = "YjUzZjE5MzktY2U2Zi00NmNiLWE3Y2ItNmUwY2M2ODE3NDA5LjBmNzcyN2I0LTNkZjgtNGQ0ZS1hNTc3LTRiMmRjOTFjOTc2ZXgxNzYyOTAwNTgxNzg3NDgwOTI5"
URL = "http://minio:9000/s3-files/662c3e99-65dc-4a26-a2c2-bbd9f4e1fac4/test_file?AWSAccessKeyId=test_username&Signature=kn3PpoJ%2BwQBYVmpYl%2B8cZK2KM0s%3D&Expires=1741791573"
RELATIVE_URL = "/s3-files/662c3e99-65dc-4a26-a2c2-bbd9f4e1fac4/test_file?AWSAccessKeyId=test_username&Signature=kn3PpoJ%2BwQBYVmpYl%2B8cZK2KM0s%3D&Expires=1741791573"
ETAG = "fac024381d213f9949facd263b44aea4"
FILE_ID = "b8a47c8d-9203-456a-aa58-ceab64b13cbb"
SIZE = 123
NAME = "test_name"
TIMESTAMP = datetime.fromisoformat("1970-01-01T00:02:03Z")


def create_repository() -> MagicMock:
    crud = MagicMock()

    crud.check_if_name_is_taken = AsyncMock()
    crud.complete_upload = AsyncMock()
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
    crud.validate_user_files = AsyncMock()
    crud.delete = AsyncMock()
    crud.delete_all = AsyncMock()
    return crud


def create_storage() -> MagicMock:
    crud = MagicMock()

    crud.initiate_upload = AsyncMock(
        return_value=response_dto.InitiateUploadResponseDTO(
            FILE_ID,
            UPLOAD_ID,
            SIZE,
            [response_dto.UploadPartResponseDTO(1, RELATIVE_URL)],
        )
    )
    crud.complete_upload = AsyncMock()
    crud.abort_upload = AsyncMock()
    crud.download = AsyncMock(return_value=RELATIVE_URL)
    crud.delete = AsyncMock()
    crud.delete_all = AsyncMock()
    return crud


def create_cache() -> MagicMock:
    cache = MagicMock()

    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()
    cache.delete = AsyncMock()
    cache.delete_many = AsyncMock()
    cache.delete_match = AsyncMock()
    return cache
