from unittest.mock import AsyncMock, MagicMock

import pytest
from grpc import StatusCode
from sqlalchemy.exc import IntegrityError

from dto import request as request_dto
from dto import response as response_dto
from repository import FileRepository

from .mocks import FILE_ID, NAME, PATH, SIZE, TIMESTAMP, USER_ID


@pytest.mark.asyncio
async def test_upload_file(mock_sessionmaker):
    dto = request_dto.UploadFileRequestDTO(USER_ID, NAME, PATH, SIZE)
    mock_session = mock_sessionmaker.return_value.__aenter__.return_value
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
    exception, expected_status, expected_message, mock_sessionmaker
):
    dto = request_dto.UploadFileRequestDTO(USER_ID, NAME, PATH, SIZE)
    mock_session = mock_sessionmaker.return_value.__aenter__.return_value
    mock_session.commit.side_effect = exception

    with pytest.raises(Exception) as exc_info:
        await FileRepository.upload_file(dto)  # type: ignore

    assert exc_info.value.args[0] == expected_status
    assert exc_info.value.args[1] == expected_message
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_file_info(mock_sessionmaker, file):
    dto = request_dto.FileOperationRequestDTO(USER_ID, FILE_ID)
    mock_session = mock_sessionmaker.return_value.__aenter__.return_value
    mock_session.get.return_value = file
    info = await FileRepository.file_info(dto)  # type: ignore

    assert isinstance(info, response_dto.FileInfoResponseDTO)
    assert info.dict() == {
        "file_id": FILE_ID,
        "user_id": USER_ID,
        "name": NAME,
        "path": PATH,
        "size": SIZE,
        "uploaded": TIMESTAMP,
    }
    mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_file_info_not_file(mock_sessionmaker):
    dto = request_dto.FileOperationRequestDTO(USER_ID, FILE_ID)
    mock_session = mock_sessionmaker.return_value.__aenter__.return_value
    mock_session.get.return_value = None

    with pytest.raises(Exception) as exc_info:
        await FileRepository.file_info(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.NOT_FOUND
    assert exc_info.value.args[1] == "File not found"
    mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_file_info_not_belongs(mock_sessionmaker, file):
    dto = request_dto.FileOperationRequestDTO(USER_ID, FILE_ID)
    mock_session = mock_sessionmaker.return_value.__aenter__.return_value
    file.user_id += "0"
    mock_session.get.return_value = file

    with pytest.raises(Exception) as exc_info:
        await FileRepository.file_info(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.NOT_FOUND
    assert exc_info.value.args[1] == "File not found"
    mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_file_info_exception(mock_sessionmaker):
    dto = request_dto.FileOperationRequestDTO(USER_ID, FILE_ID)
    mock_session = mock_sessionmaker.return_value.__aenter__.return_value
    mock_session.get.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileRepository.file_info(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_file_list(mock_sessionmaker, file):
    mock_session = mock_sessionmaker.return_value.__aenter__.return_value
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
    assert files[0].dict() == {
        "file_id": FILE_ID,
        "user_id": USER_ID,
        "name": NAME,
        "path": PATH,
        "size": SIZE,
        "uploaded": TIMESTAMP,
    }
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_file_list_exception(mock_sessionmaker):
    mock_session = mock_sessionmaker.return_value.__aenter__.return_value
    mock_session.execute.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileRepository.file_list(USER_ID)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_file_list_to_delete(mock_sessionmaker, file):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])
    mock_session = mock_sessionmaker.return_value.__aenter__.return_value
    mock_session.execute = AsyncMock(
        return_value=MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(all=MagicMock(return_value=(file,)))
            )
        )
    )

    files = await FileRepository.get_file_list_to_delete(dto)  # type: ignore

    assert isinstance(files, response_dto.DeleteFilesResponseDTO)
    assert files.dict() == {"user_id": USER_ID, "paths": [PATH]}
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_file_list_to_delete_found_less(mock_sessionmaker):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])
    mock_session = mock_sessionmaker.return_value.__aenter__.return_value
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
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_file_list_to_delete_exception(mock_sessionmaker):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])
    mock_session = mock_sessionmaker.return_value.__aenter__.return_value
    mock_session.execute.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileRepository.get_file_list_to_delete(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_delete_files(mock_sessionmaker, file):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])
    mock_session = mock_sessionmaker.return_value.__aenter__.return_value
    await FileRepository.delete_files(dto)  # type: ignore

    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_files_exception(mock_sessionmaker):
    dto = request_dto.DeleteFilesRequestDTO(USER_ID, [FILE_ID])
    mock_session = mock_sessionmaker.return_value.__aenter__.return_value
    mock_session.execute.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileRepository.delete_files(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_delete_all_files(mock_sessionmaker):
    mock_session = mock_sessionmaker.return_value.__aenter__.return_value
    await FileRepository.delete_all_files(USER_ID)  # type: ignore

    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_all_files_exception(mock_sessionmaker):
    mock_session = mock_sessionmaker.return_value.__aenter__.return_value
    mock_session.commit.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await FileRepository.delete_all_files(USER_ID)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()
