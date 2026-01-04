from unittest.mock import AsyncMock, MagicMock

import pytest
from grpc import StatusCode
from sqlalchemy.exc import IntegrityError

from dto import request as request_dto
from dto import response as response_dto
from exceptions import BaseAppException

from ..mocks import FILE_ID, NAME, SIZE, TIMESTAMP, USER_ID


@pytest.mark.asyncio
async def test_check_if_name_is_taken(session, file_repository):
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one=MagicMock(return_value=0))
    )
    dto = request_dto.InitiateUploadRequestDTO(USER_ID, NAME, SIZE)

    await file_repository.check_if_name_is_taken(dto)

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_if_name_is_taken_fail(session, file_repository):
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one=MagicMock(return_value=1))
    )
    dto = request_dto.InitiateUploadRequestDTO(USER_ID, NAME, SIZE)

    with pytest.raises(BaseAppException) as exc_info:
        await file_repository.check_if_name_is_taken(dto)

    assert exc_info.value.status_code == StatusCode.ALREADY_EXISTS
    assert exc_info.value.details == "File name is already taken"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_if_name_is_taken_exception(session, file_repository):
    session.execute.side_effect = Exception("Details")
    dto = request_dto.InitiateUploadRequestDTO(USER_ID, NAME, SIZE)

    with pytest.raises(BaseAppException) as exc_info:
        await file_repository.check_if_name_is_taken(dto)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_upload(session, file_repository):
    dto = request_dto.InitiatedUploadRequestDTO(FILE_ID, USER_ID, NAME, SIZE)

    await file_repository.complete_upload(dto)

    session.add.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, expected_status, expected_message",
    [
        (
            IntegrityError("", None, Exception("")),
            StatusCode.ALREADY_EXISTS,
            "File already exists",
        ),
        (
            Exception("Details"),
            StatusCode.INTERNAL,
            "Internal database error: Details",
        ),
    ],
)
async def test_complete_upload_exceptions(
    exception, expected_status, expected_message, session, file_repository
):
    dto = request_dto.InitiatedUploadRequestDTO(FILE_ID, USER_ID, NAME, SIZE)
    session.add = MagicMock(side_effect=exception)

    with pytest.raises(BaseAppException) as exc_info:
        await file_repository.complete_upload(dto)

    assert exc_info.value.status_code == expected_status
    assert exc_info.value.details == expected_message
    session.add.assert_called_once()


@pytest.mark.asyncio
async def test_file_info(session, file, file_repository):
    dto = request_dto.FileRequestDTO(USER_ID, FILE_ID)
    session.get.return_value = file

    info = await file_repository.file_info(dto)

    assert info == response_dto.FileInfoResponseDTO(
        FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP
    )
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_info_not_file(session, file_repository):
    dto = request_dto.FileRequestDTO(USER_ID, FILE_ID)
    session.get.return_value = None

    with pytest.raises(BaseAppException) as exc_info:
        await file_repository.file_info(dto)

    assert exc_info.value.status_code == StatusCode.NOT_FOUND
    assert exc_info.value.details == "File not found"
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_info_not_belongs(session, file, file_repository):
    dto = request_dto.FileRequestDTO(USER_ID, FILE_ID)
    file.user_id += "0"
    session.get.return_value = file

    with pytest.raises(BaseAppException) as exc_info:
        await file_repository.file_info(dto)

    assert exc_info.value.status_code == StatusCode.NOT_FOUND
    assert exc_info.value.details == "File not found"
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_info_exception(session, file_repository):
    dto = request_dto.FileRequestDTO(USER_ID, FILE_ID)
    session.get.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await file_repository.file_info(dto)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_list(session, file, file_repository):
    session.execute = AsyncMock(
        return_value=MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(all=MagicMock(return_value=(file,)))
            )
        )
    )

    files = await file_repository.file_list(USER_ID)

    assert len(files) == 1
    assert files[0] == response_dto.FileInfoResponseDTO(
        FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP
    )
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_list_exception(session, file_repository):
    session.execute.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await file_repository.file_list(USER_ID)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_user_files(session, file_repository):
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one=MagicMock(return_value=1))
    )

    await file_repository.validate_user_files(USER_ID, [FILE_ID])

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_user_files_fail(session, file_repository):
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one=MagicMock(return_value=0))
    )

    with pytest.raises(BaseAppException) as exc_info:
        await file_repository.validate_user_files(USER_ID, [FILE_ID])

    assert exc_info.value.status_code == StatusCode.NOT_FOUND
    assert exc_info.value.details == "File not found"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_user_files_exception(session, file_repository):
    session.execute.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await file_repository.validate_user_files(USER_ID, [FILE_ID])

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete(session, file_repository):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])

    await file_repository.delete(dto)

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_exception(session, file_repository):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])
    session.execute.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await file_repository.delete(dto)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_all(session, file_repository):
    session.scalars = AsyncMock(return_value=[FILE_ID])

    file_ids = await file_repository.delete_all(USER_ID)

    assert len(file_ids) == 1
    assert file_ids[0] == FILE_ID
    session.scalars.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_all_exception(session, file_repository):
    session.scalars.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await file_repository.delete_all(USER_ID)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.scalars.assert_awaited_once()
