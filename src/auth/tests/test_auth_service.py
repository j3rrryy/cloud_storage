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
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
async def test_register(mock_repository, mock_key_pair):
    dto = request_dto.RegisterRequestDTO(USERNAME, EMAIL, PASSWORD)
    response = await AuthService.register(dto)
    assert isinstance(response, str)
    mock_repository.register.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.cache", new_callable=create_cache)
@patch("service.auth_service.validate_jwt")
async def test_verify_email(mock_jwt_validator, mock_cache, mock_repository):
    await AuthService.verify_email(VERIFICATION_TOKEN)
    mock_jwt_validator.assert_called_once()
    mock_repository.verify_email.assert_called_once()
    mock_cache.delete_many.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.cache", new_callable=create_cache)
async def test_request_reset_code(mock_cache, mock_repository):
    response = await AuthService.request_reset_code(EMAIL)
    assert isinstance(response, response_dto.ResetCodeResponseDTO)
    mock_repository.profile.assert_called_once()
    mock_cache.set.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.cache", new_callable=create_cache)
async def test_validate_reset_code(mock_cache):
    dto = request_dto.ResetCodeRequestDTO(USER_ID, CODE)
    mock_cache.get.return_value = CODE
    response = await AuthService.validate_reset_code(dto)

    assert response
    mock_cache.get.assert_called_once()
    mock_cache.set.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.cache", new_callable=create_cache)
async def test_validate_reset_code_not_valid(mock_cache):
    dto = request_dto.ResetCodeRequestDTO(USER_ID, CODE)
    response = await AuthService.validate_reset_code(dto)
    assert not response
    mock_cache.get.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.cache", new_callable=create_cache)
async def test_reset_password(mock_cache, mock_repository):
    dto = request_dto.ResetPasswordRequestDTO(USER_ID, PASSWORD)
    mock_cache.get.return_value = "validated"
    await AuthService.reset_password(dto)

    mock_cache.get.assert_called_once()
    mock_repository.reset_password.assert_called_once()
    mock_cache.delete.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.cache", new_callable=create_cache)
async def test_reset_password_not_validated(mock_cache, mock_repository):
    dto = request_dto.ResetPasswordRequestDTO(USER_ID, PASSWORD)

    with pytest.raises(Exception) as exc_info:
        await AuthService.reset_password(dto)

    assert exc_info.value.args[0] == StatusCode.UNAUTHENTICATED
    assert exc_info.value.args[1] == "Code is not validated"
    mock_cache.get.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.cache", new_callable=create_cache)
async def test_log_in(mock_cache, mock_repository, mock_key_pair):
    dto = request_dto.LogInRequestDTO(USERNAME, PASSWORD, USER_IP, USER_AGENT)
    response = await AuthService.log_in(dto)

    assert isinstance(response, response_dto.LogInResponseDTO)
    mock_repository.profile.assert_called_once()
    mock_repository.log_in.assert_called_once()
    mock_cache.delete.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.cache", new_callable=create_cache)
@patch("service.auth_service.validate_jwt")
async def test_log_out(mock_jwt_validator, mock_cache, mock_repository):
    await AuthService.log_out(ACCESS_TOKEN)
    mock_jwt_validator.assert_called_once()
    mock_repository.log_out.assert_called_once()
    mock_cache.delete.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.validate_jwt")
async def test_resend_verification_mail(
    mock_jwt_validator, mock_repository, mock_key_pair
):
    response = await AuthService.resend_verification_mail(ACCESS_TOKEN)

    assert isinstance(response, response_dto.VerificationMailResponseDTO)
    mock_jwt_validator.assert_called_once()
    mock_repository.validate_access_token.assert_called_once()
    mock_repository.profile.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.validate_jwt")
async def test_auth(mock_jwt_validator, mock_repository):
    mock_jwt_validator.return_value = USER_ID
    response = await AuthService.auth(ACCESS_TOKEN)

    assert response == USER_ID
    mock_jwt_validator.assert_called_once()
    mock_repository.validate_access_token.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.cache", new_callable=create_cache)
@patch("service.auth_service.validate_jwt")
async def test_refresh(mock_jwt_validator, mock_cache, mock_repository, mock_key_pair):
    dto = request_dto.RefreshRequestDTO(REFRESH_TOKEN, USER_IP, USER_AGENT)
    response = await AuthService.refresh(dto)

    assert isinstance(response, response_dto.RefreshResponseDTO)
    mock_jwt_validator.assert_called_once()
    mock_repository.validate_refresh_token.assert_called_once()
    mock_repository.refresh.assert_called_once()
    mock_cache.delete.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.cache", new_callable=create_cache)
@patch("service.auth_service.validate_jwt")
async def test_session_list(mock_jwt_validator, mock_cache, mock_repository):
    response = await AuthService.session_list(ACCESS_TOKEN)

    assert isinstance(response, tuple)
    assert len(response) == 1
    assert isinstance(response[0], response_dto.SessionInfoResponseDTO)
    mock_jwt_validator.assert_called_once()
    mock_repository.validate_access_token.assert_called_once()
    mock_cache.get.assert_called_once()
    mock_repository.session_list.assert_called_once()
    mock_cache.set.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.cache", new_callable=create_cache)
@patch("service.auth_service.validate_jwt")
async def test_session_list_cached(mock_jwt_validator, mock_cache, mock_repository):
    mock_cache.get.return_value = mock_repository.session_list.return_value
    response = await AuthService.session_list(ACCESS_TOKEN)

    assert isinstance(response, tuple)
    assert len(response) == 1
    assert isinstance(response[0], response_dto.SessionInfoResponseDTO)
    mock_jwt_validator.assert_called_once()
    mock_repository.validate_access_token.assert_called_once()
    mock_cache.get.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.cache", new_callable=create_cache)
@patch("service.auth_service.validate_jwt")
async def test_revoke_session(mock_jwt_validator, mock_cache, mock_repository):
    dto = request_dto.RevokeSessionRequestDTO(ACCESS_TOKEN, SESSION_ID)
    await AuthService.revoke_session(dto)

    mock_jwt_validator.assert_called_once()
    mock_repository.validate_access_token.assert_called_once()
    mock_repository.validate_refresh_token.assert_called_once()
    mock_repository.revoke_session.assert_called_once()
    mock_cache.delete.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.cache", new_callable=create_cache)
@patch("service.auth_service.validate_jwt")
async def test_profile(mock_jwt_validator, mock_cache, mock_repository):
    response = await AuthService.profile(ACCESS_TOKEN)

    assert isinstance(response, response_dto.ProfileResponseDTO)
    mock_jwt_validator.assert_called_once()
    mock_repository.validate_access_token.assert_called_once()
    mock_cache.get.assert_called_once()
    mock_repository.profile.assert_called_once()
    mock_cache.set.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.cache", new_callable=create_cache)
@patch("service.auth_service.validate_jwt")
async def test_profile_cached(mock_jwt_validator, mock_cache, mock_repository):
    mock_cache.get.return_value = mock_repository.profile.return_value
    response = await AuthService.profile(ACCESS_TOKEN)

    assert isinstance(response, response_dto.ProfileResponseDTO)
    mock_jwt_validator.assert_called_once()
    mock_repository.validate_access_token.assert_called_once()
    mock_cache.get.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.cache", new_callable=create_cache)
@patch("service.auth_service.validate_jwt")
async def test_update_email(
    mock_jwt_validator, mock_cache, mock_repository, mock_key_pair
):
    dto = request_dto.UpdateEmailRequestDTO(ACCESS_TOKEN, EMAIL)
    response = await AuthService.update_email(dto)

    assert isinstance(response, response_dto.VerificationMailResponseDTO)
    mock_jwt_validator.assert_called_once()
    mock_repository.validate_access_token.assert_called_once()
    mock_repository.update_email.assert_called_once()
    mock_cache.delete_many.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.validate_jwt")
async def test_update_password(mock_jwt_validator, mock_repository):
    dto = request_dto.UpdatePasswordRequestDTO(ACCESS_TOKEN, PASSWORD, PASSWORD)
    await AuthService.update_password(dto)

    mock_jwt_validator.assert_called_once()
    mock_repository.validate_access_token.assert_called_once()
    mock_repository.update_password.assert_called_once()


@pytest.mark.asyncio
@patch("service.auth_service.AuthRepository", new_callable=create_repository)
@patch("service.auth_service.cache", new_callable=create_cache)
@patch("service.auth_service.validate_jwt")
async def test_delete_profile(mock_jwt_validator, mock_cache, mock_repository):
    mock_jwt_validator.return_value = USER_ID
    response = await AuthService.delete_profile(ACCESS_TOKEN)

    assert response == USER_ID
    mock_jwt_validator.assert_called_once()
    mock_repository.validate_access_token.assert_called_once()
    mock_repository.delete_profile.assert_called_once()
    mock_cache.delete_match.assert_called_once()
