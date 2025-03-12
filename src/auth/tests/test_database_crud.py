import pytest
from grpc import StatusCode
from sqlalchemy.exc import IntegrityError

from database import CRUD
from dto import request as request_dto
from dto import response as response_dto
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
    user_id = await CRUD.register(dto, mock_session)

    assert user_id == USER_ID
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


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
    mock_session.refresh.side_effect = exception

    with pytest.raises(Exception) as exc_info:
        await CRUD.register(dto, mock_session)

    assert exc_info.value.args[0] == expected_status
    assert exc_info.value.args[1] == expected_message
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_verify_email(mock_session):
    await CRUD.verify_email(USER_ID, mock_session)
    mock_session.get.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_verify_email_not_user(mock_session):
    mock_session.get.return_value = None

    with pytest.raises(Exception) as exc_info:
        await CRUD.verify_email(USER_ID, mock_session)

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Token is invalid"
    mock_session.get.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_verify_email_exception(mock_session):
    mock_session.commit.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await CRUD.verify_email(USER_ID, mock_session)

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.get.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_reset_password(mock_session):
    dto = request_dto.ResetPasswordRequestDTO(USER_ID, PASSWORD)
    await CRUD.reset_password(dto, mock_session)
    mock_session.get.assert_called_once()
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_reset_password_not_user(mock_session):
    dto = request_dto.ResetPasswordRequestDTO(USER_ID, PASSWORD)
    mock_session.get.return_value = None

    with pytest.raises(Exception) as exc_info:
        await CRUD.reset_password(dto, mock_session)

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Invalid credentials"
    mock_session.get.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_reset_password_exception(mock_session):
    dto = request_dto.ResetPasswordRequestDTO(USER_ID, PASSWORD)
    mock_session.commit.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await CRUD.reset_password(dto, mock_session)

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.get.assert_called_once()
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_log_in(mock_session):
    dto = request_dto.LogInDataRequestDTO(
        ACCESS_TOKEN, REFRESH_TOKEN, USER_ID, USER_IP, BROWSER
    )
    await CRUD.log_in(dto, mock_session)
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


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
        await CRUD.log_in(dto, mock_session)

    assert exc_info.value.args[0] == expected_status
    assert exc_info.value.args[1] == expected_message
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_log_out(mock_session):
    await CRUD.log_out(ACCESS_TOKEN, mock_session)
    mock_session.execute.assert_called_once()
    mock_session.delete.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_log_out_not_tokens(mock_session):
    mock_session.execute.return_value.scalar_one_or_none.return_value = None

    with pytest.raises(Exception) as exc_info:
        await CRUD.log_out(ACCESS_TOKEN, mock_session)

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Token is invalid"
    mock_session.execute.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_log_out_exception(mock_session):
    mock_session.commit.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await CRUD.log_out(ACCESS_TOKEN, mock_session)

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_called_once()
    mock_session.delete.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_refresh(mock_session):
    dto = request_dto.RefreshDataRequestDTO(
        ACCESS_TOKEN, REFRESH_TOKEN, REFRESH_TOKEN, USER_ID, USER_IP, BROWSER
    )
    await CRUD.refresh(dto, mock_session)
    mock_session.execute.assert_called_once()
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


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
        await CRUD.refresh(dto, mock_session)

    assert exc_info.value.args[0] == expected_status
    assert exc_info.value.args[1] == expected_message
    mock_session.execute.assert_called_once()
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_session_list(mock_session, token_pair):
    mock_session.execute.return_value.scalars.return_value.all.return_value = (
        token_pair,
    )
    sessions = await CRUD.session_list(USER_ID, mock_session)

    assert isinstance(sessions, tuple)
    assert len(sessions) == 1
    assert sessions[0].dict() == {
        "session_id": SESSION_ID,
        "user_id": USER_ID,
        "access_token": ACCESS_TOKEN,
        "refresh_token": REFRESH_TOKEN,
        "user_ip": USER_IP,
        "browser": BROWSER,
        "last_accessed": TIMESTAMP,
    }
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_session_list_exception(mock_session):
    mock_session.execute.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await CRUD.session_list(ACCESS_TOKEN, mock_session)

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_revoke_session(mock_session):
    await CRUD.revoke_session(SESSION_ID, mock_session)
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_revoke_session_exception(mock_session):
    mock_session.commit.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await CRUD.revoke_session(SESSION_ID, mock_session)

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_validate_access_token(mock_session):
    await CRUD.validate_access_token(ACCESS_TOKEN, mock_session)
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_validate_access_token_not_tokens(mock_session):
    mock_session.execute.return_value.scalar_one_or_none.return_value = None

    with pytest.raises(Exception) as exc_info:
        await CRUD.validate_access_token(ACCESS_TOKEN, mock_session)

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Token is invalid"
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_validate_access_token_exception(mock_session):
    mock_session.execute.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await CRUD.validate_access_token(ACCESS_TOKEN, mock_session)

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_validate_refresh_token_using_token(mock_session):
    await CRUD.validate_refresh_token(REFRESH_TOKEN, mock_session)
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_validate_refresh_token_using_session_id(mock_session):
    await CRUD.validate_refresh_token(SESSION_ID, mock_session)
    mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_validate_refresh_token_not_tokens(mock_session):
    mock_session.execute.return_value.scalar_one_or_none.return_value = None

    with pytest.raises(Exception) as exc_info:
        await CRUD.validate_refresh_token(ACCESS_TOKEN, mock_session)

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Token is invalid"
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_validate_refresh_token_exception(mock_session):
    mock_session.get.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await CRUD.validate_refresh_token(SESSION_ID, mock_session)

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_profile_using_username(mock_session, user):
    mock_session.execute.return_value.scalar_one_or_none.return_value = user
    profile = await CRUD.profile(USERNAME, mock_session)

    assert isinstance(profile, response_dto.ProfileResponseDTO)
    assert profile.dict() == {
        "user_id": USER_ID,
        "username": USERNAME,
        "email": EMAIL,
        "password": user.password,
        "verified": True,
    }
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_profile_using_email(mock_session, user):
    mock_session.execute.return_value.scalar_one_or_none.return_value = user
    profile = await CRUD.profile(EMAIL, mock_session)

    assert isinstance(profile, response_dto.ProfileResponseDTO)
    assert profile.dict() == {
        "user_id": USER_ID,
        "username": USERNAME,
        "email": EMAIL,
        "password": user.password,
        "verified": True,
    }
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_profile_using_user_id(mock_session, user):
    mock_session.get.return_value = user
    profile = await CRUD.profile(USER_ID, mock_session)

    assert isinstance(profile, response_dto.ProfileResponseDTO)
    assert profile.dict() == {
        "user_id": USER_ID,
        "username": USERNAME,
        "email": EMAIL,
        "password": user.password,
        "verified": True,
    }
    mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_profile_not_user(mock_session):
    mock_session.get.return_value = None

    with pytest.raises(Exception) as exc_info:
        await CRUD.profile(USER_ID, mock_session)

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Invalid credentials"
    mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_profile_exception(mock_session):
    mock_session.execute.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await CRUD.profile(EMAIL, mock_session)

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_update_email(mock_session, user):
    dto = request_dto.UpdateEmailDataRequestDTO(USER_ID, ACCESS_TOKEN, EMAIL)
    mock_session.get.return_value = user
    username = await CRUD.update_email(dto, mock_session)

    assert username == USERNAME
    mock_session.get.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_update_email_not_user(mock_session):
    dto = request_dto.UpdateEmailDataRequestDTO(USER_ID, ACCESS_TOKEN, EMAIL)
    mock_session.get.return_value = None

    with pytest.raises(Exception) as exc_info:
        await CRUD.update_email(dto, mock_session)

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Invalid credentials"
    mock_session.get.assert_called_once()
    mock_session.rollback.assert_called_once()


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
    mock_session.refresh.side_effect = exception

    with pytest.raises(Exception) as exc_info:
        await CRUD.update_email(dto, mock_session)

    assert exc_info.value.args[0] == expected_status
    assert exc_info.value.args[1] == expected_message
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_update_password(mock_session, user):
    dto = request_dto.UpdatePasswordDataRequestDTO(
        USER_ID, ACCESS_TOKEN, PASSWORD, get_hashed_password(PASSWORD)
    )
    mock_session.get.return_value = user
    await CRUD.update_password(dto, mock_session)

    mock_session.get.assert_called_once()
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_password_not_user(mock_session):
    dto = request_dto.UpdatePasswordDataRequestDTO(
        USER_ID, ACCESS_TOKEN, PASSWORD, get_hashed_password(PASSWORD)
    )
    mock_session.get.return_value = None

    with pytest.raises(Exception) as exc_info:
        await CRUD.update_password(dto, mock_session)

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Invalid credentials"
    mock_session.get.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_update_password_exception(mock_session, user):
    dto = request_dto.UpdatePasswordDataRequestDTO(
        USER_ID, ACCESS_TOKEN, PASSWORD, get_hashed_password(PASSWORD)
    )
    mock_session.get.return_value = user
    mock_session.commit.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await CRUD.update_password(dto, mock_session)

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.get.assert_called_once()
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_delete_profile(mock_session):
    mock_session.execute.return_value.rowcount = 1
    await CRUD.delete_profile(USER_ID, mock_session)
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_profile_row_count(mock_session):
    mock_session.execute.return_value.rowcount = 0

    with pytest.raises(Exception) as exc_info:
        await CRUD.delete_profile(USER_ID, mock_session)

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Invalid credentials"
    mock_session.execute.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_delete_profile_exception(mock_session):
    mock_session.execute.return_value.rowcount = 1
    mock_session.commit.side_effect = Exception("Details")

    with pytest.raises(Exception) as exc_info:
        await CRUD.delete_profile(USER_ID, mock_session)

    assert exc_info.value.args[0] == StatusCode.INTERNAL
    assert exc_info.value.args[1] == "Internal database error, Details"
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()
