from unittest.mock import AsyncMock, MagicMock

import pytest
from grpc import StatusCode
from sqlalchemy.exc import IntegrityError

from dto import request as request_dto
from dto import response as response_dto
from exceptions import BaseAppException
from security import get_jwt_hash, get_password_hash

from ..mocks import (
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
async def test_register(session, auth_repository):
    dto = request_dto.RegisterRequestDTO(USERNAME, EMAIL, PASSWORD)
    session.add.side_effect = lambda user: setattr(user, "user_id", USER_ID)

    user_id = await auth_repository.register(dto)

    assert user_id == USER_ID
    session.add.assert_called_once()
    session.flush.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, expected_status, expected_message",
    [
        (
            IntegrityError("", None, Exception("")),
            StatusCode.ALREADY_EXISTS,
            "User already exists",
        ),
        (Exception("Details"), StatusCode.INTERNAL, "Internal database error: Details"),
    ],
)
async def test_register_exceptions(
    exception, expected_status, expected_message, session, auth_repository
):
    dto = request_dto.RegisterRequestDTO(USERNAME, EMAIL, PASSWORD)
    session.flush.side_effect = exception

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.register(dto)

    assert exc_info.value.status_code == expected_status
    assert exc_info.value.details == expected_message
    session.add.assert_called_once()
    session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_confirm_email(session, user, auth_repository):
    session.get.return_value = user

    await auth_repository.confirm_email(USER_ID)

    assert user.email_confirmed
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_confirm_email_not_user(session, auth_repository):
    session.get.return_value = None

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.confirm_email(USER_ID)

    assert exc_info.value.status_code == StatusCode.UNAUTHENTICATED
    assert exc_info.value.details == "Invalid credentials"
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_confirm_email_exception(session, auth_repository):
    session.get.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.confirm_email(USER_ID)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_reset_password(session, user, auth_repository):
    new_password = get_password_hash(PASSWORD + "0")
    dto = request_dto.ResetPasswordRequestDTO(USER_ID, new_password)
    session.get.return_value = user
    session.scalars = AsyncMock(return_value=[ACCESS_TOKEN])

    deleted_access_tokens = await auth_repository.reset_password(dto)

    assert deleted_access_tokens == [ACCESS_TOKEN]
    assert user.password == new_password
    session.get.assert_awaited_once()
    session.scalars.assert_awaited_once()


@pytest.mark.asyncio
async def test_reset_password_not_user(session, auth_repository):
    dto = request_dto.ResetPasswordRequestDTO(USER_ID, PASSWORD)
    session.get.return_value = None

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.reset_password(dto)

    assert exc_info.value.status_code == StatusCode.UNAUTHENTICATED
    assert exc_info.value.details == "Invalid credentials"
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_reset_password_exception(session, auth_repository):
    dto = request_dto.ResetPasswordRequestDTO(USER_ID, PASSWORD)
    session.scalars.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.reset_password(dto)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.get.assert_awaited_once()
    session.scalars.assert_awaited_once()


@pytest.mark.asyncio
async def test_log_in(auth_repository, session):
    dto = request_dto.LogInDataRequestDTO(
        get_jwt_hash(ACCESS_TOKEN),
        get_jwt_hash(REFRESH_TOKEN),
        USER_ID,
        USER_IP,
        BROWSER,
    )

    await auth_repository.log_in(dto)

    session.add.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, expected_status, expected_message",
    [
        (
            IntegrityError("", None, Exception("")),
            StatusCode.ALREADY_EXISTS,
            "Token already exists",
        ),
        (Exception("Details"), StatusCode.INTERNAL, "Internal database error: Details"),
    ],
)
async def test_log_in_exceptions(
    exception, expected_status, expected_message, session, auth_repository
):
    dto = request_dto.LogInDataRequestDTO(
        get_jwt_hash(ACCESS_TOKEN),
        get_jwt_hash(REFRESH_TOKEN),
        USER_ID,
        USER_IP,
        BROWSER,
    )
    session.add = MagicMock(side_effect=exception)

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.log_in(dto)

    assert exc_info.value.status_code == expected_status
    assert exc_info.value.details == expected_message
    session.add.assert_called_once()


@pytest.mark.asyncio
async def test_log_out(session, auth_repository):
    hashed_access_token = get_jwt_hash(ACCESS_TOKEN)
    session.execute = AsyncMock(return_value=MagicMock(rowcount=1))

    await auth_repository.log_out(hashed_access_token)

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_log_out_not_tokens(session, auth_repository):
    hashed_access_token = get_jwt_hash(ACCESS_TOKEN)
    session.execute = AsyncMock(return_value=MagicMock(rowcount=0))

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.log_out(hashed_access_token)

    assert exc_info.value.status_code == StatusCode.UNAUTHENTICATED
    assert exc_info.value.details == "Token is invalid"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_log_out_exception(session, auth_repository):
    hashed_access_token = get_jwt_hash(ACCESS_TOKEN)
    session.execute.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.log_out(hashed_access_token)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh(session, auth_repository):
    dto = request_dto.RefreshDataRequestDTO(
        get_jwt_hash(ACCESS_TOKEN),
        get_jwt_hash(REFRESH_TOKEN),
        get_jwt_hash(REFRESH_TOKEN),
        USER_ID,
        USER_IP,
        BROWSER,
    )
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=ACCESS_TOKEN))
    )

    deleted_access_token = await auth_repository.refresh(dto)

    assert deleted_access_token == ACCESS_TOKEN
    session.execute.assert_awaited_once()
    session.add.assert_called_once()


@pytest.mark.asyncio
async def test_refresh_not_tokens(session, auth_repository):
    dto = request_dto.RefreshDataRequestDTO(
        get_jwt_hash(ACCESS_TOKEN),
        get_jwt_hash(REFRESH_TOKEN),
        get_jwt_hash(REFRESH_TOKEN),
        USER_ID,
        USER_IP,
        BROWSER,
    )
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.refresh(dto)

    assert exc_info.value.status_code == StatusCode.UNAUTHENTICATED
    assert exc_info.value.details == "Token is invalid"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, expected_status, expected_message",
    [
        (
            IntegrityError("", None, Exception("")),
            StatusCode.ALREADY_EXISTS,
            "Token already exists",
        ),
        (Exception("Details"), StatusCode.INTERNAL, "Internal database error: Details"),
    ],
)
async def test_refresh_exceptions(
    exception, expected_status, expected_message, session, auth_repository
):
    dto = request_dto.RefreshDataRequestDTO(
        get_jwt_hash(ACCESS_TOKEN),
        get_jwt_hash(REFRESH_TOKEN),
        get_jwt_hash(REFRESH_TOKEN),
        USER_ID,
        USER_IP,
        BROWSER,
    )
    session.add = MagicMock(side_effect=exception)

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.refresh(dto)

    assert exc_info.value.status_code == expected_status
    assert exc_info.value.details == expected_message
    session.execute.assert_awaited_once()
    session.add.assert_called_once()


@pytest.mark.asyncio
async def test_session_list(session, token_pair, auth_repository):
    session.scalars = AsyncMock(return_value=[token_pair])

    sessions = await auth_repository.session_list(USER_ID)

    assert sessions == [
        response_dto.SessionInfoResponseDTO(
            SESSION_ID,
            USER_ID,
            ACCESS_TOKEN,
            REFRESH_TOKEN,
            USER_IP,
            BROWSER,
            TIMESTAMP,
        )
    ]
    session.scalars.assert_awaited_once()


@pytest.mark.asyncio
async def test_session_list_exception(session, auth_repository):
    session.scalars.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.session_list(ACCESS_TOKEN)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.scalars.assert_awaited_once()


@pytest.mark.asyncio
async def test_revoke_session(session, auth_repository):
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=ACCESS_TOKEN))
    )

    deleted_access_token = await auth_repository.revoke_session(SESSION_ID)

    assert deleted_access_token == ACCESS_TOKEN
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_revoke_session_not_tokens(session, auth_repository):
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.revoke_session(SESSION_ID)

    assert exc_info.value.status_code == StatusCode.NOT_FOUND
    assert exc_info.value.details == "Session not found"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_revoke_session_exception(session, auth_repository):
    session.execute.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.revoke_session(SESSION_ID)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_access_token(session, auth_repository):
    session.execute = AsyncMock(
        return_value=MagicMock(scalar=MagicMock(return_value=True))
    )

    await auth_repository.validate_access_token(ACCESS_TOKEN)

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_access_token_not_tokens(session, auth_repository):
    session.execute = AsyncMock(
        return_value=MagicMock(scalar=MagicMock(return_value=False))
    )

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.validate_access_token(ACCESS_TOKEN)

    assert exc_info.value.status_code == StatusCode.UNAUTHENTICATED
    assert exc_info.value.details == "Token is invalid"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_access_token_exception(session, auth_repository):
    session.execute.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.validate_access_token(ACCESS_TOKEN)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_profile_by_user_id(session, user, auth_repository):
    session.get.return_value = user

    profile = await auth_repository.profile_by_user_id(USER_ID)

    assert profile == response_dto.ProfileResponseDTO(
        user.user_id,
        user.username,
        user.email,
        user.password,
        user.email_confirmed,
        user.registered_at,
    )
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_profile_by_user_id_not_user(session, auth_repository):
    session.get.return_value = None

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.profile_by_user_id(USER_ID)

    assert exc_info.value.status_code == StatusCode.UNAUTHENTICATED
    assert exc_info.value.details == "Invalid credentials"
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_profile_by_user_id_exception(session, auth_repository):
    session.get.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.profile_by_user_id(USER_ID)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_profile_by_username(session, user, auth_repository):
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=user))
    )

    profile = await auth_repository.profile_by_username(USERNAME)

    assert profile == response_dto.ProfileResponseDTO(
        user.user_id,
        user.username,
        user.email,
        user.password,
        user.email_confirmed,
        user.registered_at,
    )
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_profile_by_username_not_user(session, auth_repository):
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.profile_by_username(USERNAME)

    assert exc_info.value.status_code == StatusCode.UNAUTHENTICATED
    assert exc_info.value.details == "Invalid credentials"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_profile_by_username_exception(session, auth_repository):
    session.execute.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.profile_by_username(USERNAME)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_profile_by_email(session, user, auth_repository):
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=user))
    )

    profile = await auth_repository.profile_by_email(EMAIL)

    assert profile == response_dto.ProfileResponseDTO(
        user.user_id,
        user.username,
        user.email,
        user.password,
        user.email_confirmed,
        user.registered_at,
    )
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_profile_by_email_not_user(session, auth_repository):
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.profile_by_email(EMAIL)

    assert exc_info.value.status_code == StatusCode.UNAUTHENTICATED
    assert exc_info.value.details == "Invalid credentials"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_profile_by_email_exception(session, auth_repository):
    session.execute.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.profile_by_email(EMAIL)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_email(session, user, auth_repository):
    new_email = EMAIL + "0"
    dto = request_dto.UpdateEmailDataRequestDTO(USER_ID, new_email)
    user.email_confirmed = True
    session.get.return_value = user

    username = await auth_repository.update_email(dto)

    assert username == USERNAME
    assert user.email == new_email
    assert not user.email_confirmed
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_email_not_user(session, auth_repository):
    dto = request_dto.UpdateEmailDataRequestDTO(USER_ID, EMAIL)
    session.get.return_value = None

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.update_email(dto)

    assert exc_info.value.status_code == StatusCode.UNAUTHENTICATED
    assert exc_info.value.details == "Invalid credentials"
    session.get.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, expected_status, expected_message",
    [
        (
            IntegrityError("", None, Exception("")),
            StatusCode.ALREADY_EXISTS,
            "Email address is already in use",
        ),
        (Exception("Details"), StatusCode.INTERNAL, "Internal database error: Details"),
    ],
)
async def test_update_email_exceptions(
    exception, expected_status, expected_message, session, auth_repository
):
    dto = request_dto.UpdateEmailDataRequestDTO(USER_ID, EMAIL)
    session.get.side_effect = exception

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.update_email(dto)

    assert exc_info.value.status_code == expected_status
    assert exc_info.value.details == expected_message
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_password(session, user, auth_repository):
    new_password = get_password_hash(PASSWORD + "0")
    dto = request_dto.UpdatePasswordDataRequestDTO(USER_ID, new_password)
    session.get.return_value = user
    session.scalars = AsyncMock(return_value=[ACCESS_TOKEN])

    deleted_access_tokens = await auth_repository.update_password(dto)

    assert deleted_access_tokens == [ACCESS_TOKEN]
    assert user.password == new_password
    session.get.assert_awaited_once()
    session.scalars.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_password_not_user(session, auth_repository):
    dto = request_dto.UpdatePasswordDataRequestDTO(USER_ID, PASSWORD)
    session.get.return_value = None

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.update_password(dto)

    assert exc_info.value.status_code == StatusCode.UNAUTHENTICATED
    assert exc_info.value.details == "Invalid credentials"
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_password_exception(session, auth_repository):
    dto = request_dto.UpdatePasswordDataRequestDTO(USER_ID, PASSWORD)
    session.scalars.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.update_password(dto)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.get.assert_awaited_once()
    session.scalars.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_profile(session, auth_repository):
    session.scalars = AsyncMock(return_value=[ACCESS_TOKEN])
    session.execute = AsyncMock(return_value=MagicMock(rowcount=1))

    deleted_access_tokens = await auth_repository.delete_profile(USER_ID)

    assert deleted_access_tokens == [ACCESS_TOKEN]
    session.scalars.assert_awaited_once()
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_profile_not_user(session, auth_repository):
    session.execute = AsyncMock(return_value=MagicMock(rowcount=0))

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.delete_profile(USER_ID)

    assert exc_info.value.status_code == StatusCode.UNAUTHENTICATED
    assert exc_info.value.details == "Invalid credentials"
    session.scalars.assert_awaited_once()
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_profile_exception(session, auth_repository):
    session.execute.side_effect = Exception("Details")

    with pytest.raises(BaseAppException) as exc_info:
        await auth_repository.delete_profile(USER_ID)

    assert exc_info.value.status_code == StatusCode.INTERNAL
    assert exc_info.value.details == "Internal database error: Details"
    session.scalars.assert_awaited_once()
    session.execute.assert_awaited_once()
