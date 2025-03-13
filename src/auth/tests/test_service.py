from unittest.mock import patch

import pytest
from grpc import StatusCode

from dto import request as request_dto
from dto import response as response_dto
from service import AuthService

from .mocks import (
    ACCESS_TOKEN,
    CODE,
    EMAIL,
    PASSWORD,
    REFRESH_TOKEN,
    SESSION_ID,
    USER_AGENT,
    USER_ID,
    USER_IP,
    USERNAME,
    VERIFICATION_TOKEN,
    create_cache,
    create_repository,
)


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
async def test_register(mock_crud):
    dto = request_dto.RegisterRequestDTO(USERNAME, EMAIL, PASSWORD)
    response = await AuthService.register(dto)  # type: ignore
    assert isinstance(response, response_dto.VerificationMailResponseDTO)
    mock_crud.register.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.cache", new_callable=create_cache)
@patch("service.auth.validate_jwt")
async def test_verify_email(mock_jwt_validator, mock_cache, mock_crud):
    await AuthService.verify_email(VERIFICATION_TOKEN)  # type: ignore
    mock_jwt_validator.assert_called_once()
    mock_crud.verify_email.assert_called_once()
    mock_cache.delete_many.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.cache", new_callable=create_cache)
async def test_request_reset_code(mock_cache, mock_crud):
    response = await AuthService.request_reset_code(EMAIL)  # type: ignore
    assert isinstance(response, response_dto.ResetCodeResponseDTO)
    mock_crud.profile.assert_called_once()
    mock_cache.set.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.cache", new_callable=create_cache)
async def test_validate_reset_code(mock_cache):
    dto = request_dto.ResetCodeRequestDTO(USER_ID, CODE)
    mock_cache.get.return_value = CODE
    response = await AuthService.validate_reset_code(dto)  # type: ignore

    assert response
    mock_cache.get.assert_called_once()
    mock_cache.set.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.cache", new_callable=create_cache)
async def test_validate_reset_code_not_valid(mock_cache):
    dto = request_dto.ResetCodeRequestDTO(USER_ID, CODE)
    response = await AuthService.validate_reset_code(dto)  # type: ignore
    assert not response
    mock_cache.get.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.cache", new_callable=create_cache)
async def test_reset_password(mock_cache, mock_crud):
    dto = request_dto.ResetPasswordRequestDTO(USER_ID, PASSWORD)
    mock_cache.get.return_value = "validated"
    await AuthService.reset_password(dto)  # type: ignore

    mock_cache.get.assert_called_once()
    mock_crud.reset_password.assert_called_once()
    mock_cache.delete.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.cache", new_callable=create_cache)
async def test_reset_password_not_validated(mock_cache, mock_crud):
    dto = request_dto.ResetPasswordRequestDTO(USER_ID, PASSWORD)

    with pytest.raises(Exception) as exc_info:
        await AuthService.reset_password(dto)  # type: ignore

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Code is not validated"
    mock_cache.get.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.cache", new_callable=create_cache)
async def test_log_in(mock_cache, mock_crud):
    dto = request_dto.LogInRequestDTO(USERNAME, PASSWORD, USER_IP, USER_AGENT)
    response = await AuthService.log_in(dto)  # type: ignore

    assert isinstance(response, response_dto.LogInResponseDTO)
    mock_crud.profile.assert_called_once()
    mock_crud.log_in.assert_called_once()
    mock_cache.delete.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.cache", new_callable=create_cache)
@patch("service.auth.validate_jwt")
async def test_log_out(mock_jwt_validator, mock_cache, mock_crud):
    await AuthService.log_out(ACCESS_TOKEN)  # type: ignore
    mock_jwt_validator.assert_called_once()
    mock_crud.log_out.assert_called_once()
    mock_cache.delete.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.validate_jwt")
async def test_resend_verification_mail(mock_jwt_validator, mock_crud):
    response = await AuthService.resend_verification_mail(ACCESS_TOKEN)  # type: ignore

    assert isinstance(response, response_dto.VerificationMailResponseDTO)
    mock_jwt_validator.assert_called_once()
    mock_crud.validate_access_token.assert_called_once()
    mock_crud.profile.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.validate_jwt")
async def test_auth(mock_jwt_validator, mock_crud):
    mock_jwt_validator.return_value = USER_ID
    response = await AuthService.auth(ACCESS_TOKEN)  # type: ignore

    assert response == USER_ID
    mock_jwt_validator.assert_called_once()
    mock_crud.validate_access_token.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.cache", new_callable=create_cache)
@patch("service.auth.validate_jwt")
async def test_refresh(mock_jwt_validator, mock_cache, mock_crud):
    dto = request_dto.RefreshRequestDTO(REFRESH_TOKEN, USER_IP, USER_AGENT)
    response = await AuthService.refresh(dto)  # type: ignore

    assert isinstance(response, response_dto.RefreshResponseDTO)
    mock_jwt_validator.assert_called_once()
    mock_crud.validate_refresh_token.assert_called_once()
    mock_crud.refresh.assert_called_once()
    mock_cache.delete.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.cache", new_callable=create_cache)
@patch("service.auth.validate_jwt")
async def test_session_list(mock_jwt_validator, mock_cache, mock_crud):
    response = await AuthService.session_list(ACCESS_TOKEN)  # type: ignore

    assert isinstance(response, tuple)
    assert len(response) == 1
    assert isinstance(response[0], response_dto.SessionInfoResponseDTO)
    mock_jwt_validator.assert_called_once()
    mock_crud.validate_access_token.assert_called_once()
    mock_cache.get.assert_called_once()
    mock_crud.session_list.assert_called_once()
    mock_cache.set.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.cache", new_callable=create_cache)
@patch("service.auth.validate_jwt")
async def test_session_list_cached(mock_jwt_validator, mock_cache, mock_crud):
    mock_cache.get.return_value = mock_crud.session_list.return_value
    response = await AuthService.session_list(ACCESS_TOKEN)  # type: ignore

    assert isinstance(response, tuple)
    assert len(response) == 1
    assert isinstance(response[0], response_dto.SessionInfoResponseDTO)
    mock_jwt_validator.assert_called_once()
    mock_crud.validate_access_token.assert_called_once()
    mock_cache.get.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.cache", new_callable=create_cache)
@patch("service.auth.validate_jwt")
async def test_revoke_session(mock_jwt_validator, mock_cache, mock_crud):
    dto = request_dto.RevokeSessionRequestDTO(ACCESS_TOKEN, SESSION_ID)
    await AuthService.revoke_session(dto)  # type: ignore

    mock_jwt_validator.assert_called_once()
    mock_crud.validate_access_token.assert_called_once()
    mock_crud.validate_refresh_token.assert_called_once()
    mock_crud.revoke_session.assert_called_once()
    mock_cache.delete.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.cache", new_callable=create_cache)
@patch("service.auth.validate_jwt")
async def test_profile(mock_jwt_validator, mock_cache, mock_crud):
    response = await AuthService.profile(ACCESS_TOKEN)  # type: ignore

    assert isinstance(response, response_dto.ProfileResponseDTO)
    mock_jwt_validator.assert_called_once()
    mock_crud.validate_access_token.assert_called_once()
    mock_cache.get.assert_called_once()
    mock_crud.profile.assert_called_once()
    mock_cache.set.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.cache", new_callable=create_cache)
@patch("service.auth.validate_jwt")
async def test_profile_cached(mock_jwt_validator, mock_cache, mock_crud):
    mock_cache.get.return_value = mock_crud.profile.return_value
    response = await AuthService.profile(ACCESS_TOKEN)  # type: ignore

    assert isinstance(response, response_dto.ProfileResponseDTO)
    mock_jwt_validator.assert_called_once()
    mock_crud.validate_access_token.assert_called_once()
    mock_cache.get.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.cache", new_callable=create_cache)
@patch("service.auth.validate_jwt")
async def test_update_email(mock_jwt_validator, mock_cache, mock_crud):
    dto = request_dto.UpdateEmailRequestDTO(ACCESS_TOKEN, EMAIL)
    response = await AuthService.update_email(dto)  # type: ignore

    assert isinstance(response, response_dto.VerificationMailResponseDTO)
    mock_jwt_validator.assert_called_once()
    mock_crud.validate_access_token.assert_called_once()
    mock_crud.update_email.assert_called_once()
    mock_cache.delete_many.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.validate_jwt")
async def test_update_password(mock_jwt_validator, mock_crud):
    dto = request_dto.UpdatePasswordRequestDTO(ACCESS_TOKEN, PASSWORD, PASSWORD)
    await AuthService.update_password(dto)  # type: ignore

    mock_jwt_validator.assert_called_once()
    mock_crud.validate_access_token.assert_called_once()
    mock_crud.update_password.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth.AuthRepository", new_callable=create_repository)
@patch("service.auth.cache", new_callable=create_cache)
@patch("service.auth.validate_jwt")
async def test_delete_profile(mock_jwt_validator, mock_cache, mock_crud):
    mock_jwt_validator.return_value = USER_ID
    response = await AuthService.delete_profile(ACCESS_TOKEN)  # type: ignore

    assert response == USER_ID
    mock_jwt_validator.assert_called_once()
    mock_crud.validate_access_token.assert_called_once()
    mock_crud.delete_profile.assert_called_once()
    mock_cache.delete_match.assert_called_once()
