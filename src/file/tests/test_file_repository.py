from unittest.mock import AsyncMock, MagicMock

import pytest
from grpc import StatusCode
from sqlalchemy.exc import IntegrityError

from dto import request as request_dto
from dto import response as response_dto
from repository import FileRepository

from .mocks import FILE_ID, NAME, PATH, SIZE, TIMESTAMP, USER_ID


@pytest.mark.asyncio
async def test_upload_file(mock_session):
    dto = request_dto.UploadFileRequestDTO(USER_ID, NAME, PATH, SIZE)
    await FileRepository.upload_file(dto)  # type: ignore

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
async def test_upload_file_exceptions(
    exception, expected_status, expected_message, mock_session
):
    dto = request_dto.UploadFileRequestDTO(USER_ID, NAME, PATH, SIZE)
    mock_session.commit.side_effect = exception

    with pytest.raises(Exception) as exc_info:
        await FileRepository.upload_file(dto)  # type: ignore

    assert exc_info.value.args[0] == expected_status
    assert exc_info.value.args[1] == expected_message
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_info(mock_session, file):
    dto = request_dto.FileOperationRequestDTO(USER_ID, FILE_ID)
    mock_session.get.return_value = file
    info = await FileRepository.file_info(dto)  # type: ignore

    assert info == response_dto.FileInfoResponseDTO(
        FILE_ID, USER_ID, NAME, PATH, SIZE, TIMESTAMP
    )
    mock_session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_info_not_file(mock_session):
    dto = request_dto.FileOperationRequestDTO(USER_ID, FILE_ID)
    mock_session.get.return_value = None

    with pytest.raises(Exception) as exc_info:
        await FileRepository.file_info(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.NOT_FOUND
    assert exc_info.value.args[1] == "File not found"
    mock_session.get.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_info_not_belongs(mock_session, file):
    dto = request_dto.FileOperationRequestDTO(USER_ID, FILE_ID)
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
    dto = request_dto.FileOperationRequestDTO(USER_ID, FILE_ID)
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

    assert isinstance(files, tuple)
    assert len(files) == 1
    assert files[0] == response_dto.FileInfoResponseDTO(
        FILE_ID, USER_ID, NAME, PATH, SIZE, TIMESTAMP
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
async def test_get_file_list_to_delete(mock_session, file):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])
    mock_session.execute = AsyncMock(
        return_value=MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(all=MagicMock(return_value=(file,)))
            )
        )
    )

    files = await FileRepository.get_file_list_to_delete(dto)  # type: ignore
    assert files == response_dto.DeleteFilesResponseDTO(USER_ID, [PATH])
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_file_list_to_delete_found_less(mock_session):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])
    mock_session.execute = AsyncMock(
        return_value=MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(all=MagicMock(return_value=tuple()))
            )
        )
    )

    with pytest.raises(Exception) as exc_info:
        await FileRepository.get_file_list_to_delete(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.NOT_FOUND
    assert exc_info.value.args[1] == "One or more files not found"
    mock_session.execute.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_file_list_to_delete_exception(mock_session):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])
    mock_session.execute.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileRepository.get_file_list_to_delete(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_files(mock_session, file):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])
    await FileRepository.delete_files(dto)  # type: ignore

    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_files_exception(mock_session):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])
    mock_session.execute.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileRepository.delete_files(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_all_files(mock_session):
    await FileRepository.delete_all_files(USER_ID)  # type: ignore

    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_all_files_exception(mock_session):
    mock_session.commit.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileRepository.delete_all_files(USER_ID)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()
