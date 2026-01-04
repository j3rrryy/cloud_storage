from time import time

from cashews import cache
from grpc import StatusCode

from dto import request as request_dto
from dto import response as response_dto
from enums import ResetCodeStatus, TokenTypes
from exceptions import EmailHasAlreadyBeenConfirmedException, UnauthenticatedException
from repository import AuthRepository
from utils import (
    access_token_key,
    compare_passwords,
    convert_user_agent,
    generate_jwt,
    generate_reset_code,
    get_hashed_jwt,
    get_hashed_password,
    user_all_keys,
    user_profile_key,
    user_reset_key,
    user_session_list_key,
    validate_jwt,
    validate_jwt_and_get_user_id,
)


class AuthService:
    MIN_CACHE_TTL = 5

    @staticmethod
    async def register(
        data: request_dto.RegisterRequestDTO,
    ) -> str:
        data = data.replace(password=get_hashed_password(data.password))
        user_id = await AuthRepository.register(data)
        return generate_jwt(user_id, TokenTypes.EMAIL_CONFIRMATION)

    @staticmethod
    async def confirm_email(token: str) -> None:
        user_id = validate_jwt_and_get_user_id(token, TokenTypes.EMAIL_CONFIRMATION)
        await AuthRepository.confirm_email(user_id)
        await cache.delete(user_profile_key(user_id))

    @staticmethod
    async def request_reset_code(email: str) -> response_dto.ResetCodeResponseDTO:
        profile = await AuthRepository.profile(email)
        code = generate_reset_code()
        await cache.set(user_reset_key(profile.user_id), code, 600)
        return response_dto.ResetCodeResponseDTO(
            profile.user_id, profile.username, code
        )

    @staticmethod
    async def validate_reset_code(data: request_dto.ResetCodeRequestDTO) -> bool:
        reset_key = user_reset_key(data.user_id)
        code = await cache.get(reset_key)

        if not code or data.code != code:
            return False

        await cache.set(reset_key, ResetCodeStatus.VALIDATED.value, 600)
        return True

    @classmethod
    async def reset_password(cls, data: request_dto.ResetPasswordRequestDTO) -> None:
        reset_key = user_reset_key(data.user_id)
        code = await cache.get(reset_key)

        if not code or code != ResetCodeStatus.VALIDATED.value:
            raise UnauthenticatedException(
                StatusCode.UNAUTHENTICATED, "Code is not validated"
            )

        data = data.replace(new_password=get_hashed_password(data.new_password))
        deleted_access_tokens = await AuthRepository.reset_password(data)
        await cls._delete_cached_access_tokens(*deleted_access_tokens)
        await cache.delete_many(user_session_list_key(data.user_id), reset_key)

    @staticmethod
    async def log_in(
        data: request_dto.LogInRequestDTO,
    ) -> response_dto.LogInResponseDTO:
        profile = await AuthRepository.profile(data.username)
        compare_passwords(data.password, profile.password)

        access_token = generate_jwt(profile.user_id, TokenTypes.ACCESS)
        refresh_token = generate_jwt(profile.user_id, TokenTypes.REFRESH)
        browser = convert_user_agent(data.user_agent)

        hashed_access_token = get_hashed_jwt(access_token)
        hashed_refresh_token = get_hashed_jwt(refresh_token)
        dto = request_dto.LogInDataRequestDTO(
            hashed_access_token,
            hashed_refresh_token,
            profile.user_id,
            data.user_ip,
            browser,
        )

        await AuthRepository.log_in(dto)
        await cache.delete(user_session_list_key(profile.user_id))
        return response_dto.LogInResponseDTO(
            access_token, refresh_token, profile.email, browser, profile.email_confirmed
        )

    @classmethod
    async def log_out(cls, access_token: str) -> None:
        hashed_access_token = get_hashed_jwt(access_token)
        user_id = await cls._cached_access_token(access_token)
        await AuthRepository.log_out(hashed_access_token)
        await cls._delete_cached_access_tokens(hashed_access_token)
        await cache.delete(user_session_list_key(user_id))

    @classmethod
    async def resend_email_confirmation_mail(
        cls, access_token: str
    ) -> response_dto.EmailConfirmationMailResponseDTO:
        user_id = await cls._cached_access_token(access_token)
        profile = await AuthRepository.profile(user_id)

        if profile.email_confirmed:
            raise EmailHasAlreadyBeenConfirmedException(
                StatusCode.ALREADY_EXISTS, "Email has already been confirmed"
            )

        token = generate_jwt(user_id, TokenTypes.EMAIL_CONFIRMATION)
        return response_dto.EmailConfirmationMailResponseDTO(
            token, profile.username, profile.email
        )

    @classmethod
    async def auth(cls, access_token: str) -> str:
        return await cls._cached_access_token(access_token)

    @classmethod
    async def refresh(
        cls, data: request_dto.RefreshRequestDTO
    ) -> response_dto.RefreshResponseDTO:
        user_id = validate_jwt_and_get_user_id(data.refresh_token, TokenTypes.REFRESH)

        access_token = generate_jwt(user_id, TokenTypes.ACCESS)
        refresh_token = generate_jwt(user_id, TokenTypes.REFRESH)
        browser = convert_user_agent(data.user_agent)

        hashed_access_token = get_hashed_jwt(access_token)
        hashed_refresh_token = get_hashed_jwt(refresh_token)
        hashed_old_refresh_token = get_hashed_jwt(data.refresh_token)
        dto = request_dto.RefreshDataRequestDTO(
            hashed_access_token,
            hashed_refresh_token,
            hashed_old_refresh_token,
            user_id,
            data.user_ip,
            browser,
        )

        deleted_access_token = await AuthRepository.refresh(dto)
        await cls._delete_cached_access_tokens(deleted_access_token)
        await cache.delete(user_session_list_key(user_id))
        return response_dto.RefreshResponseDTO(access_token, refresh_token)

    @classmethod
    async def session_list(
        cls, access_token: str
    ) -> list[response_dto.SessionInfoResponseDTO]:
        user_id = await cls._cached_access_token(access_token)
        session_list_key = user_session_list_key(user_id)

        if cached := await cache.get(session_list_key):
            return cached

        sessions = await AuthRepository.session_list(user_id)
        await cache.set(session_list_key, sessions, 3600)
        return sessions

    @classmethod
    async def revoke_session(cls, data: request_dto.RevokeSessionRequestDTO) -> None:
        user_id = await cls._cached_access_token(data.access_token)
        deleted_access_token = await AuthRepository.revoke_session(data.session_id)
        await cls._delete_cached_access_tokens(deleted_access_token)
        await cache.delete(user_session_list_key(user_id))

    @classmethod
    async def profile(cls, access_token: str) -> response_dto.ProfileResponseDTO:
        user_id = await cls._cached_access_token(access_token)
        profile_key = user_profile_key(user_id)

        if cached := await cache.get(profile_key):
            return cached

        profile = await AuthRepository.profile(user_id)
        await cache.set(profile_key, profile, 3600)
        return profile

    @classmethod
    async def update_email(
        cls, data: request_dto.UpdateEmailRequestDTO
    ) -> response_dto.EmailConfirmationMailResponseDTO:
        user_id = await cls._cached_access_token(data.access_token)
        dto = request_dto.UpdateEmailDataRequestDTO(user_id, data.new_email)

        username = await AuthRepository.update_email(dto)
        await cache.delete(user_profile_key(user_id))
        token = generate_jwt(user_id, TokenTypes.EMAIL_CONFIRMATION)
        return response_dto.EmailConfirmationMailResponseDTO(
            token, username, data.new_email
        )

    @classmethod
    async def update_password(cls, data: request_dto.UpdatePasswordRequestDTO) -> None:
        user_id = await cls._cached_access_token(data.access_token)
        dto = request_dto.UpdatePasswordDataRequestDTO(
            user_id, data.old_password, get_hashed_password(data.new_password)
        )
        deleted_access_tokens = await AuthRepository.update_password(dto)
        await cls._delete_cached_access_tokens(*deleted_access_tokens)

    @classmethod
    async def delete_profile(cls, access_token: str) -> str:
        user_id = await cls._cached_access_token(access_token)
        deleted_access_tokens = await AuthRepository.delete_profile(user_id)
        await cls._delete_cached_access_tokens(*deleted_access_tokens)
        await cache.delete_many(*user_all_keys(user_id))
        return user_id

    @classmethod
    async def _cached_access_token(cls, access_token: str) -> str:
        hashed_access_token = get_hashed_jwt(access_token)
        key = access_token_key(hashed_access_token)
        if cached := await cache.get(key):
            return cached

        jwt = validate_jwt(access_token, TokenTypes.ACCESS)
        await AuthRepository.validate_access_token(hashed_access_token)

        ttl = jwt.exp - int(time())
        if ttl > cls.MIN_CACHE_TTL:
            await cache.set(key, jwt.subject, ttl)

        return jwt.subject

    @staticmethod
    async def _delete_cached_access_tokens(*hashed_access_tokens: str) -> None:
        if hashed_access_tokens:
            keys = (
                access_token_key(access_token) for access_token in hashed_access_tokens
            )
            await cache.delete_many(*keys)
