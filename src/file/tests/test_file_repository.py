from unittest.mock import AsyncMock, MagicMock

import pytest
from grpc import StatusCode
from sqlalchemy.exc import IntegrityError

from dto import request as request_dto
from dto import response as response_dto
from repository import FileRepository

from .mocks import FILE_ID, NAME, SIZE, TIMESTAMP, USER_ID


@pytest.mark.asyncio
async def test_check_if_name_is_taken(mock_session):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one=MagicMock(return_value=0))
    )
    dto = request_dto.InitiateUploadRequestDTO(USER_ID, NAME, SIZE)
    await FileRepository.check_if_name_is_taken(dto)  # type: ignore
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_if_name_is_taken_fail(mock_session):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one=MagicMock(return_value=1))
    )
    dto = request_dto.InitiateUploadRequestDTO(USER_ID, NAME, SIZE)

    with pytest.raises(Exception) as exc_info:
        await FileRepository.check_if_name_is_taken(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.ALREADY_EXISTS
    assert exc_info.value.args[1] == "File name is already taken"
    mock_session.execute.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_if_name_is_taken_exception(mock_session):
    mock_session.execute.side_effect = Exception("Details")
    dto = request_dto.InitiateUploadRequestDTO(USER_ID, NAME, SIZE)

    with pytest.raises(Exception) as exc_info:
        await FileRepository.check_if_name_is_taken(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_upload(mock_session):
    dto = request_dto.InitiatedUploadRequestDTO(FILE_ID, USER_ID, NAME, SIZE)
    await FileRepository.complete_upload(dto)  # type: ignore
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, expected_status, expected_message",
    [
        (
            IntegrityError("", None, Exception("")),
            StatusCode.ALREADY_EXISTS,
            "File already exists",
        ),
        (Exception("Details"), StatusCode.INTERNAL, "Internal database error, Details"),
    ],
)
async def test_complete_upload_exceptions(
    exception, expected_status, expected_message, mock_session
):
    dto = request_dto.InitiatedUploadRequestDTO(FILE_ID, USER_ID, NAME, SIZE)
    mock_session.commit.side_effect = exception

    with pytest.raises(Exception) as exc_info:
        await FileRepository.complete_upload(dto)  # type: ignore

    assert exc_info.value.args[0] == expected_status
    assert exc_info.value.args[1] == expected_message
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_info(mock_session, file):
    dto = request_dto.FileRequestDTO(USER_ID, FILE_ID)
    mock_session.get.return_value = file
    info = await FileRepository.file_info(dto)  # type: ignore

    assert info == response_dto.FileInfoResponseDTO(
        FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP
    )
    mock_session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_info_not_file(mock_session):
    dto = request_dto.FileRequestDTO(USER_ID, FILE_ID)
    mock_session.get.return_value = None

    with pytest.raises(Exception) as exc_info:
        await FileRepository.file_info(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.NOT_FOUND
    assert exc_info.value.args[1] == "File not found"
    mock_session.get.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_info_not_belongs(mock_session, file):
    dto = request_dto.FileRequestDTO(USER_ID, FILE_ID)
    file.user_id += "0"
    mock_session.get.return_value = file

    with pytest.raises(Exception) as exc_info:
        await FileRepository.file_info(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.NOT_FOUND
    assert exc_info.value.args[1] == "File not found"
    mock_session.get.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_info_exception(mock_session):
    dto = request_dto.FileRequestDTO(USER_ID, FILE_ID)
    mock_session.get.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileRepository.file_info(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.get.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_list(mock_session, file):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(all=MagicMock(return_value=(file,)))
            )
        )
    )
    files = await FileRepository.file_list(USER_ID)  # type: ignore

    assert len(files) == 1
    assert files[0] == response_dto.FileInfoResponseDTO(
        FILE_ID, USER_ID, NAME, SIZE, TIMESTAMP
    )
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_list_exception(mock_session):
    mock_session.execute.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileRepository.file_list(USER_ID)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_user_files(mock_session):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one=MagicMock(return_value=1))
    )
    await FileRepository.validate_user_files(USER_ID, [FILE_ID])  # type: ignore
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_user_files_fail(mock_session):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one=MagicMock(return_value=0))
    )

    with pytest.raises(Exception) as exc_info:
        await FileRepository.validate_user_files(USER_ID, [FILE_ID])  # type: ignore

    assert exc_info.value.args[0] == StatusCode.NOT_FOUND
    assert exc_info.value.args[1] == "One or more files not found"
    mock_session.execute.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_user_files_exception(mock_session):
    mock_session.execute.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileRepository.validate_user_files(USER_ID, [FILE_ID])  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete(mock_session):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])
    await FileRepository.delete(dto)  # type: ignore
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_exception(mock_session):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])
    mock_session.commit.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileRepository.delete(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_all(mock_session):
    await FileRepository.delete_all(USER_ID)  # type: ignore
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_all_exception(mock_session):
    mock_session.commit.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileRepository.delete_all(USER_ID)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()
