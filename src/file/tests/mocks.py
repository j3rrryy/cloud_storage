from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from dto import response as response_dto

PATH = "/"
SIZE = 123
NAME = "test_name"
USER_ID = "00e51a90-0f94-4ecb-8dd1-399ba409508e"
FILE_ID = "b8a47c8d-9203-456a-aa58-ceab64b13cbb"
TIMESTAMP = datetime.fromisoformat("1970-01-01T00:02:03Z")
URL = "http://minio:9000/file/662c3e99-65dc-4a26-a2c2-bbd9f4e1fac4/test_file?AWSAccessKeyId=test_username&Signature=kn3PpoJ%2BwQBYVmpYl%2B8cZK2KM0s%3D&Expires=1741791573"
RELATIVE_URL = "/file/662c3e99-65dc-4a26-a2c2-bbd9f4e1fac4/test_file?AWSAccessKeyId=test_username&Signature=kn3PpoJ%2BwQBYVmpYl%2B8cZK2KM0s%3D&Expires=1741791573"


def create_repository() -> MagicMock:
    crud = MagicMock()

    crud.upload_file = AsyncMock()
    crud.file_info = AsyncMock(
        return_value=response_dto.FileInfoResponseDTO(
            FILE_ID, USER_ID, NAME, PATH + NAME, SIZE, TIMESTAMP
        )
    )
    crud.file_list = AsyncMock(
        return_value=(
            response_dto.FileInfoResponseDTO(
                FILE_ID, USER_ID, NAME, PATH + NAME, SIZE, TIMESTAMP
            ),
        )
    )
    crud.get_file_list_to_delete = AsyncMock(
        return_value=response_dto.DeleteFilesResponseDTO(USER_ID, [PATH])
    )
    crud.delete_files = AsyncMock()
    crud.delete_all_files = AsyncMock()
    return crud


def create_storage() -> MagicMock:
    crud = MagicMock()

    crud.upload_file = AsyncMock(return_value=URL)
    crud.download_file = AsyncMock(return_value=URL)
    crud.delete_files = AsyncMock()
    crud.delete_all_files = AsyncMock()
    return crud


def create_cache() -> MagicMock:
    cache = MagicMock()

    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()
    cache.delete = AsyncMock()
    cache.delete_many = AsyncMock()
    cache.delete_match = AsyncMock()
    return cache
