from unittest.mock import ANY, AsyncMock, MagicMock

import pytest
from grpc import StatusCode
from sqlalchemy.exc import IntegrityError

from dto import request as request_dto
from dto import response as response_dto
from repository import AuthRepository
from utils import get_hashed_password

from .mocks import (
    ACCESS_TOKEN,
    BROWSER,
    EMAIL,
    PASSWORD,
    REFRESH_TOKEN,
    SESSION_ID,
    TIMESTAMP,
    USER_ID,
    USER_IP,
    USERNAME,
)


@pytest.mark.asyncio
async def test_register(mock_session):
    dto = request_dto.RegisterRequestDTO(USERNAME, EMAIL, PASSWORD)
    mock_session.refresh.side_effect = lambda user: setattr(user, "user_id", USER_ID)
    user_id = await AuthRepository.register(dto)  # type: ignore

    assert user_id == USER_ID
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, expected_status, expected_message",
    [
        (
            IntegrityError("", None, Exception("")),
            StatusCode.ALREADY_EXISTS,
            "User already exists",
        ),
        (Exception("Details"), StatusCode.INTERNAL, "Internal database error, Details"),
    ],
)
async def test_register_exceptions(
    exception, expected_status, expected_message, mock_session
):
    dto = request_dto.RegisterRequestDTO(USERNAME, EMAIL, PASSWORD)
    mock_session.commit.side_effect = exception

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.register(dto)  # type: ignore

    assert exc_info.value.args[0] == expected_status
    assert exc_info.value.args[1] == expected_message
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_verify_email(mock_session):
    await AuthRepository.verify_email(USER_ID)  # type: ignore

    mock_session.get.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_verify_email_not_user(mock_session):
    mock_session.get.return_value = None

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.verify_email(USER_ID)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Token is invalid"
    mock_session.get.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_verify_email_exception(mock_session):
    mock_session.commit.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.verify_email(USER_ID)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.get.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_reset_password(mock_session):
    dto = request_dto.ResetPasswordRequestDTO(USER_ID, PASSWORD)
    mock_session.scalars = AsyncMock(return_value=(ACCESS_TOKEN,))
    deleted_access_tokens = await AuthRepository.reset_password(dto)  # type: ignore

    assert isinstance(deleted_access_tokens, tuple)
    assert len(deleted_access_tokens) == 1
    assert deleted_access_tokens[0] == ACCESS_TOKEN
    mock_session.get.assert_awaited_once()
    mock_session.scalars.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_reset_password_not_user(mock_session):
    dto = request_dto.ResetPasswordRequestDTO(USER_ID, PASSWORD)
    mock_session.get.return_value = None

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.reset_password(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Invalid credentials"
    mock_session.get.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_reset_password_exception(mock_session):
    dto = request_dto.ResetPasswordRequestDTO(USER_ID, PASSWORD)
    mock_session.commit.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.reset_password(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.get.assert_awaited_once()
    mock_session.scalars.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_log_in(mock_session):
    dto = request_dto.LogInDataRequestDTO(
        ACCESS_TOKEN, REFRESH_TOKEN, USER_ID, USER_IP, BROWSER
    )
    await AuthRepository.log_in(dto)  # type: ignore

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, expected_status, expected_message",
    [
        (
            IntegrityError("", None, Exception("")),
            StatusCode.ALREADY_EXISTS,
            "Token already exists",
        ),
        (Exception("Details"), StatusCode.INTERNAL, "Internal database error, Details"),
    ],
)
async def test_log_in_exceptions(
    exception, expected_status, expected_message, mock_session
):
    dto = request_dto.LogInDataRequestDTO(
        ACCESS_TOKEN, REFRESH_TOKEN, USER_ID, USER_IP, BROWSER
    )
    mock_session.commit.side_effect = exception

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.log_in(dto)  # type: ignore

    assert exc_info.value.args[0] == expected_status
    assert exc_info.value.args[1] == expected_message
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_log_out(mock_session):
    await AuthRepository.log_out(ACCESS_TOKEN)  # type: ignore

    mock_session.execute.assert_awaited_once()
    mock_session.delete.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_log_out_not_tokens(mock_session):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.log_out(ACCESS_TOKEN)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Token is invalid"
    mock_session.execute.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_log_out_exception(mock_session):
    mock_session.commit.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.log_out(ACCESS_TOKEN)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_awaited_once()
    mock_session.delete.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh(mock_session):
    dto = request_dto.RefreshDataRequestDTO(
        ACCESS_TOKEN, REFRESH_TOKEN, REFRESH_TOKEN, USER_ID, USER_IP, BROWSER
    )
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=ACCESS_TOKEN))
    )
    deleted_access_token = await AuthRepository.refresh(dto)  # type: ignore

    assert deleted_access_token == ACCESS_TOKEN
    mock_session.execute.assert_awaited_once()
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh_not_tokens(mock_session):
    dto = request_dto.RefreshDataRequestDTO(
        ACCESS_TOKEN, REFRESH_TOKEN, REFRESH_TOKEN, USER_ID, USER_IP, BROWSER
    )
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.refresh(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Token is invalid"
    mock_session.execute.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, expected_status, expected_message",
    [
        (
            IntegrityError("", None, Exception("")),
            StatusCode.ALREADY_EXISTS,
            "Token already exists",
        ),
        (Exception("Details"), StatusCode.INTERNAL, "Internal database error, Details"),
    ],
)
async def test_refresh_exceptions(
    exception, expected_status, expected_message, mock_session
):
    dto = request_dto.RefreshDataRequestDTO(
        ACCESS_TOKEN, REFRESH_TOKEN, REFRESH_TOKEN, USER_ID, USER_IP, BROWSER
    )
    mock_session.commit.side_effect = exception

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.refresh(dto)  # type: ignore

    assert exc_info.value.args[0] == expected_status
    assert exc_info.value.args[1] == expected_message
    mock_session.execute.assert_awaited_once()
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_session_list(mock_session, token_pair):
    mock_session.scalars = AsyncMock(return_value=(token_pair,))
    sessions = await AuthRepository.session_list(USER_ID)  # type: ignore

    assert isinstance(sessions, tuple)
    assert len(sessions) == 1
    assert sessions[0] == response_dto.SessionInfoResponseDTO(
        SESSION_ID, USER_ID, ACCESS_TOKEN, REFRESH_TOKEN, USER_IP, BROWSER, TIMESTAMP
    )
    mock_session.scalars.assert_awaited_once()


@pytest.mark.asyncio
async def test_session_list_exception(mock_session):
    mock_session.scalars.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.session_list(ACCESS_TOKEN)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.scalars.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_revoke_session(mock_session):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=ACCESS_TOKEN))
    )
    deleted_access_token = await AuthRepository.revoke_session(SESSION_ID)  # type: ignore

    assert deleted_access_token == ACCESS_TOKEN
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_revoke_session_not_tokens(mock_session):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.revoke_session(SESSION_ID)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.NOT_FOUND
    assert exc_info.value.args[1] == "Session ID not found"
    mock_session.execute.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_revoke_session_exception(mock_session):
    mock_session.commit.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.revoke_session(SESSION_ID)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_access_token(mock_session):
    await AuthRepository.validate_access_token(ACCESS_TOKEN)  # type: ignore

    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_access_token_not_tokens(mock_session):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.validate_access_token(ACCESS_TOKEN)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Token is invalid"
    mock_session.execute.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_access_token_exception(mock_session):
    mock_session.execute.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.validate_access_token(ACCESS_TOKEN)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_profile_using_username(mock_session, user):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=user))
    )
    profile = await AuthRepository.profile(USERNAME)  # type: ignore

    assert profile == response_dto.ProfileResponseDTO(
        USER_ID, USERNAME, EMAIL, user.password, True, ANY
    )
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_profile_using_email(mock_session, user):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=user))
    )
    profile = await AuthRepository.profile(EMAIL)  # type: ignore

    assert profile == response_dto.ProfileResponseDTO(
        USER_ID, USERNAME, EMAIL, user.password, True, ANY
    )
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_profile_using_user_id(mock_session, user):
    mock_session.get.return_value = user
    profile = await AuthRepository.profile(USER_ID)  # type: ignore

    assert profile == response_dto.ProfileResponseDTO(
        USER_ID, USERNAME, EMAIL, user.password, True, ANY
    )
    mock_session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_profile_not_user(mock_session):
    mock_session.get.return_value = None

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.profile(USER_ID)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Invalid credentials"
    mock_session.get.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_profile_exception(mock_session):
    mock_session.execute.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.profile(EMAIL)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_email(mock_session, user):
    dto = request_dto.UpdateEmailDataRequestDTO(USER_ID, ACCESS_TOKEN, EMAIL)
    mock_session.get.return_value = user
    username = await AuthRepository.update_email(dto)  # type: ignore

    assert username == USERNAME
    mock_session.get.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_email_not_user(mock_session):
    dto = request_dto.UpdateEmailDataRequestDTO(USER_ID, ACCESS_TOKEN, EMAIL)
    mock_session.get.return_value = None

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.update_email(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Invalid credentials"
    mock_session.get.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, expected_status, expected_message",
    [
        (
            IntegrityError("", None, Exception("")),
            StatusCode.ALREADY_EXISTS,
            "Email address is already in use",
        ),
        (Exception("Details"), StatusCode.INTERNAL, "Internal database error, Details"),
    ],
)
async def test_update_email_exceptions(
    exception, expected_status, expected_message, mock_session
):
    dto = request_dto.UpdateEmailDataRequestDTO(USER_ID, ACCESS_TOKEN, EMAIL)
    mock_session.commit.side_effect = exception

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.update_email(dto)  # type: ignore

    assert exc_info.value.args[0] == expected_status
    assert exc_info.value.args[1] == expected_message
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_password(mock_session, user):
    dto = request_dto.UpdatePasswordDataRequestDTO(
        USER_ID, ACCESS_TOKEN, PASSWORD, get_hashed_password(PASSWORD)
    )
    mock_session.get.return_value = user
    mock_session.scalars = AsyncMock(return_value=(ACCESS_TOKEN,))
    deleted_access_tokens = await AuthRepository.update_password(dto)  # type: ignore

    assert isinstance(deleted_access_tokens, tuple)
    assert len(deleted_access_tokens) == 1
    assert deleted_access_tokens[0] == ACCESS_TOKEN
    mock_session.get.assert_awaited_once()
    mock_session.scalars.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_password_not_user(mock_session):
    dto = request_dto.UpdatePasswordDataRequestDTO(
        USER_ID, ACCESS_TOKEN, PASSWORD, get_hashed_password(PASSWORD)
    )
    mock_session.get.return_value = None

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.update_password(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Invalid credentials"
    mock_session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_password_exception(mock_session, user):
    dto = request_dto.UpdatePasswordDataRequestDTO(
        USER_ID, ACCESS_TOKEN, PASSWORD, get_hashed_password(PASSWORD)
    )
    mock_session.get.return_value = user
    mock_session.commit.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.update_password(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.get.assert_awaited_once()
    mock_session.scalars.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_profile(mock_session):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(all=MagicMock(return_value=((None, ACCESS_TOKEN),)))
    )
    deleted_access_tokens = await AuthRepository.delete_profile(USER_ID)  # type: ignore

    assert isinstance(deleted_access_tokens, tuple)
    assert len(deleted_access_tokens) == 1
    assert deleted_access_tokens[0] == ACCESS_TOKEN
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_profile_zero_rows(mock_session):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(all=MagicMock(return_value=()))
    )

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.delete_profile(USER_ID)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Invalid credentials"
    mock_session.execute.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_profile_exception(mock_session):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(all=MagicMock(return_value=((None, ACCESS_TOKEN),)))
    )
    mock_session.commit.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await AuthRepository.delete_profile(USER_ID)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()
