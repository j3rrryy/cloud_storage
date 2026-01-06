from time import time
from typing import Any

from cashews import Cache

from dto import request as request_dto
from dto import response as response_dto
from enums import ResetCodeStatus, TokenTypes
from exceptions import EmailHasAlreadyBeenConfirmedException, UnauthenticatedException
from protocols import AuthRepositoryProtocol, AuthServiceProtocol
from security import (
    compare_passwords,
    generate_code,
    generate_jwt,
    get_jwt_hash,
    get_password_hash,
    validate_jwt,
    validate_jwt_and_get_user_id,
)
from settings import Settings
from utils import (
    access_token_key,
    convert_user_agent,
    user_all_keys,
    user_profile_key,
    user_reset_key,
    user_session_list_key,
)


class AuthService(AuthServiceProtocol):
    def __init__(self, auth_repository: AuthRepositoryProtocol, cache: Cache):
        self._auth_repository = auth_repository
        self._cache = cache

    async def register(self, data: request_dto.RegisterRequestDTO) -> str:
        data = data.replace(password=get_password_hash(data.password))
        user_id = await self._auth_repository.register(data)
        return generate_jwt(user_id, TokenTypes.EMAIL_CONFIRMATION)

    async def confirm_email(self, token: str) -> None:
        user_id = validate_jwt_and_get_user_id(token, TokenTypes.EMAIL_CONFIRMATION)
        await self._auth_repository.confirm_email(user_id)
        await self._cache.delete(user_profile_key(user_id))

    async def request_reset_code(self, email: str) -> response_dto.ResetCodeResponseDTO:
        profile = await self._auth_repository.profile_by_email(email)
        code = generate_code()
        await self._cache.set(user_reset_key(profile.user_id), code, 600)
        return response_dto.ResetCodeResponseDTO(
            profile.user_id, profile.username, code
        )

    async def validate_reset_code(self, data: request_dto.ResetCodeRequestDTO) -> bool:
        reset_key = user_reset_key(data.user_id)
        code = await self._cache.get(reset_key)
        if not code or data.code != code:
            return False
        await self._cache.set(reset_key, ResetCodeStatus.VALIDATED.value, 600)
        return True

    async def reset_password(self, data: request_dto.ResetPasswordRequestDTO) -> None:
        reset_key = user_reset_key(data.user_id)
        code = await self._cache.get(reset_key)

        if not code or code != ResetCodeStatus.VALIDATED.value:
            raise UnauthenticatedException("Code is not validated")

        data = data.replace(new_password=get_password_hash(data.new_password))
        deleted_access_tokens = await self._auth_repository.reset_password(data)
        await self._invalidate_sessions_cache(data.user_id, *deleted_access_tokens)
        await self._cache.delete(reset_key)

    async def log_in(
        self, data: request_dto.LogInRequestDTO
    ) -> response_dto.LogInResponseDTO:
        profile = await self._auth_repository.profile_by_username(data.username)
        compare_passwords(profile.password, data.password)

        access_token = generate_jwt(profile.user_id, TokenTypes.ACCESS)
        refresh_token = generate_jwt(profile.user_id, TokenTypes.REFRESH)
        browser = convert_user_agent(data.user_agent)

        hashed_access_token = get_jwt_hash(access_token)
        hashed_refresh_token = get_jwt_hash(refresh_token)
        dto = request_dto.LogInDataRequestDTO(
            hashed_access_token,
            hashed_refresh_token,
            profile.user_id,
            data.user_ip,
            browser,
        )

        await self._auth_repository.log_in(dto)
        await self._cache.delete(user_session_list_key(profile.user_id))
        return response_dto.LogInResponseDTO(
            access_token, refresh_token, profile.email, browser, profile.email_confirmed
        )

    async def log_out(self, access_token: str) -> None:
        hashed_access_token = get_jwt_hash(access_token)
        user_id = await self._cached_access_token(access_token)
        await self._auth_repository.log_out(hashed_access_token)
        await self._invalidate_sessions_cache(user_id, hashed_access_token)

    async def resend_email_confirmation_mail(
        self, access_token: str
    ) -> response_dto.EmailConfirmationMailResponseDTO:
        user_id = await self._cached_access_token(access_token)
        profile = await self._auth_repository.profile_by_user_id(user_id)

        if profile.email_confirmed:
            raise EmailHasAlreadyBeenConfirmedException

        token = generate_jwt(user_id, TokenTypes.EMAIL_CONFIRMATION)
        return response_dto.EmailConfirmationMailResponseDTO(
            token, profile.username, profile.email
        )

    async def auth(self, access_token: str) -> str:
        return await self._cached_access_token(access_token)

    async def refresh(
        self, data: request_dto.RefreshRequestDTO
    ) -> response_dto.RefreshResponseDTO:
        user_id = validate_jwt_and_get_user_id(data.refresh_token, TokenTypes.REFRESH)

        access_token = generate_jwt(user_id, TokenTypes.ACCESS)
        refresh_token = generate_jwt(user_id, TokenTypes.REFRESH)
        browser = convert_user_agent(data.user_agent)

        hashed_access_token = get_jwt_hash(access_token)
        hashed_refresh_token = get_jwt_hash(refresh_token)
        hashed_old_refresh_token = get_jwt_hash(data.refresh_token)
        dto = request_dto.RefreshDataRequestDTO(
            hashed_access_token,
            hashed_refresh_token,
            hashed_old_refresh_token,
            user_id,
            data.user_ip,
            browser,
        )

        deleted_access_token = await self._auth_repository.refresh(dto)
        await self._invalidate_sessions_cache(user_id, deleted_access_token)
        return response_dto.RefreshResponseDTO(access_token, refresh_token)

    async def session_list(
        self, access_token: str
    ) -> list[response_dto.SessionInfoResponseDTO]:
        user_id = await self._cached_access_token(access_token)
        session_list_key = user_session_list_key(user_id)
        sessions = await self._get_cached(
            session_list_key, self._auth_repository.session_list, user_id
        )
        return sessions

    async def revoke_session(self, data: request_dto.RevokeSessionRequestDTO) -> None:
        user_id = await self._cached_access_token(data.access_token)
        deleted_access_token = await self._auth_repository.revoke_session(
            data.session_id
        )
        await self._invalidate_sessions_cache(user_id, deleted_access_token)

    async def profile(self, access_token: str) -> response_dto.ProfileResponseDTO:
        user_id = await self._cached_access_token(access_token)
        profile_key = user_profile_key(user_id)
        profile = await self._get_cached(
            profile_key, self._auth_repository.profile_by_user_id, user_id
        )
        return profile

    async def update_email(
        self, data: request_dto.UpdateEmailRequestDTO
    ) -> response_dto.EmailConfirmationMailResponseDTO:
        user_id = await self._cached_access_token(data.access_token)
        dto = request_dto.UpdateEmailDataRequestDTO(user_id, data.new_email)

        username = await self._auth_repository.update_email(dto)
        await self._cache.delete(user_profile_key(user_id))
        token = generate_jwt(user_id, TokenTypes.EMAIL_CONFIRMATION)
        return response_dto.EmailConfirmationMailResponseDTO(
            token, username, data.new_email
        )

    async def update_password(self, data: request_dto.UpdatePasswordRequestDTO) -> None:
        user_id = await self._cached_access_token(data.access_token)
        profile = await self._auth_repository.profile_by_user_id(user_id)
        compare_passwords(profile.password, data.old_password)

        dto = request_dto.UpdatePasswordDataRequestDTO(
            user_id, get_password_hash(data.new_password)
        )
        deleted_access_tokens = await self._auth_repository.update_password(dto)
        await self._invalidate_sessions_cache(user_id, *deleted_access_tokens)

    async def delete_profile(self, access_token: str) -> str:
        user_id = await self._cached_access_token(access_token)
        deleted_access_tokens = await self._auth_repository.delete_profile(user_id)
        await self._invalidate_access_tokens_cache(*deleted_access_tokens)
        await self._cache.delete_many(*user_all_keys(user_id))
        return user_id

    async def _cached_access_token(self, access_token: str) -> str:
        hashed_access_token = get_jwt_hash(access_token)
        key = access_token_key(hashed_access_token)
        if cached := await self._cache.get(key):
            return cached

        jwt = validate_jwt(access_token, TokenTypes.ACCESS)
        await self._auth_repository.validate_access_token(hashed_access_token)

        ttl = jwt.exp - int(time())
        if ttl > Settings.MIN_ACCESS_TOKEN_CACHE_TTL:
            await self._cache.set(key, jwt.subject, ttl)

        return jwt.subject  # type: ignore

    async def _get_cached(
        self, key: str, getter, *args, ttl: int = 3600, **kwargs
    ) -> Any:
        if cached := await self._cache.get(key):
            return cached
        value = await getter(*args, **kwargs)
        await self._cache.set(key, value, ttl)
        return value

    async def _invalidate_sessions_cache(
        self, user_id: str, *hashed_access_tokens: str
    ) -> None:
        await self._invalidate_access_tokens_cache(*hashed_access_tokens)
        await self._cache.delete(user_session_list_key(user_id))

    async def _invalidate_access_tokens_cache(self, *hashed_access_tokens: str) -> None:
        if hashed_access_tokens:
            keys = (
                access_token_key(access_token) for access_token in hashed_access_tokens
            )
            await self._cache.delete_many(*keys)
