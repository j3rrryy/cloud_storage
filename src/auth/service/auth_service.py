from time import time

from cashews import cache
from grpc import StatusCode

from dto import request as request_dto
from dto import response as response_dto
from enums import ResetCodeStatus, TokenTypes
from exceptions import UnauthenticatedException
from repository import AuthRepository
from utils import (
    access_token_key,
    compare_passwords,
    convert_user_agent,
    generate_jwt,
    generate_reset_code,
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
        user_id = await AuthRepository.register(data)  # type: ignore
        return generate_jwt(user_id, TokenTypes.VERIFICATION)  # type: ignore

    @staticmethod
    async def verify_email(verification_token: str) -> None:
        user_id = validate_jwt_and_get_user_id(
            verification_token, TokenTypes.VERIFICATION
        )
        await AuthRepository.verify_email(user_id)  # type: ignore
        await cache.delete(user_profile_key(user_id))

    @staticmethod
    async def request_reset_code(email: str) -> response_dto.ResetCodeResponseDTO:
        profile = await AuthRepository.profile(email)  # type: ignore
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
        deleted_access_tokens = await AuthRepository.reset_password(data)  # type: ignore
        await cls._delete_cached_access_tokens(*deleted_access_tokens)
        await cache.delete_many(user_session_list_key(data.user_id), reset_key)

    @staticmethod
    async def log_in(
        data: request_dto.LogInRequestDTO,
    ) -> response_dto.LogInResponseDTO:
        profile = await AuthRepository.profile(data.username)  # type: ignore
        compare_passwords(data.password, profile.password)  # type: ignore

        access_token = generate_jwt(profile.user_id, TokenTypes.ACCESS)  # type: ignore
        refresh_token = generate_jwt(profile.user_id, TokenTypes.REFRESH)  # type: ignore
        browser = convert_user_agent(data.user_agent)

        dto = request_dto.LogInDataRequestDTO(
            access_token, refresh_token, profile.user_id, data.user_ip, browser
        )

        await AuthRepository.log_in(dto)  # type: ignore
        await cache.delete(user_session_list_key(profile.user_id))
        return response_dto.LogInResponseDTO(
            access_token, refresh_token, profile.email, browser, profile.verified
        )

    @classmethod
    async def log_out(cls, access_token: str) -> None:
        user_id = await cls._cached_access_token(access_token)
        await AuthRepository.log_out(access_token)  # type: ignore
        await cls._delete_cached_access_tokens(access_token)
        await cache.delete(user_session_list_key(user_id))

    @classmethod
    async def resend_verification_mail(
        cls, access_token: str
    ) -> response_dto.VerificationMailResponseDTO:
        user_id = await cls._cached_access_token(access_token)
        profile = await AuthRepository.profile(user_id)  # type: ignore
        verification_token = generate_jwt(user_id, TokenTypes.VERIFICATION)  # type: ignore
        return response_dto.VerificationMailResponseDTO(
            verification_token, profile.username, profile.email
        )

    @classmethod
    async def auth(cls, access_token: str) -> str:
        user_id = await cls._cached_access_token(access_token)
        return user_id

    @classmethod
    async def refresh(
        cls, data: request_dto.RefreshRequestDTO
    ) -> response_dto.RefreshResponseDTO:
        user_id = validate_jwt_and_get_user_id(data.refresh_token, TokenTypes.REFRESH)
        access_token = generate_jwt(user_id, TokenTypes.ACCESS)  # type: ignore
        refresh_token = generate_jwt(user_id, TokenTypes.REFRESH)  # type: ignore
        browser = convert_user_agent(data.user_agent)
        dto = request_dto.RefreshDataRequestDTO(
            access_token,
            refresh_token,
            data.refresh_token,
            user_id,
            data.user_ip,
            browser,
        )

        deleted_access_token = await AuthRepository.refresh(dto)  # type: ignore
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

        sessions = await AuthRepository.session_list(user_id)  # type: ignore
        await cache.set(session_list_key, sessions, 3600)
        return sessions

    @classmethod
    async def revoke_session(cls, data: request_dto.RevokeSessionRequestDTO) -> None:
        user_id = await cls._cached_access_token(data.access_token)
        deleted_access_token = await AuthRepository.revoke_session(data.session_id)  # type: ignore
        await cls._delete_cached_access_tokens(deleted_access_token)
        await cache.delete(user_session_list_key(user_id))

    @classmethod
    async def profile(cls, access_token: str) -> response_dto.ProfileResponseDTO:
        user_id = await cls._cached_access_token(access_token)
        profile_key = user_profile_key(user_id)

        if cached := await cache.get(profile_key):
            return cached

        profile = await AuthRepository.profile(user_id)  # type: ignore
        await cache.set(profile_key, profile, 3600)
        return profile

    @classmethod
    async def update_email(
        cls, data: request_dto.UpdateEmailRequestDTO
    ) -> response_dto.VerificationMailResponseDTO:
        user_id = await cls._cached_access_token(data.access_token)
        dto = request_dto.UpdateEmailDataRequestDTO(
            user_id, data.access_token, data.new_email
        )

        username = await AuthRepository.update_email(dto)  # type: ignore
        await cache.delete(user_profile_key(user_id))
        verification_token = generate_jwt(user_id, TokenTypes.VERIFICATION)  # type: ignore
        return response_dto.VerificationMailResponseDTO(
            verification_token, username, data.new_email
        )

    @classmethod
    async def update_password(cls, data: request_dto.UpdatePasswordRequestDTO) -> None:
        user_id = await cls._cached_access_token(data.access_token)
        dto = request_dto.UpdatePasswordDataRequestDTO(
            user_id,
            data.access_token,
            data.old_password,
            get_hashed_password(data.new_password),
        )
        deleted_access_tokens = await AuthRepository.update_password(dto)  # type: ignore
        await cls._delete_cached_access_tokens(*deleted_access_tokens)

    @classmethod
    async def delete_profile(cls, access_token: str) -> str:
        user_id = await cls._cached_access_token(access_token)
        deleted_access_tokens = await AuthRepository.delete_profile(user_id)  # type: ignore
        await cls._delete_cached_access_tokens(*deleted_access_tokens)
        await cache.delete_many(*user_all_keys(user_id))
        return user_id

    @classmethod
    async def _cached_access_token(cls, access_token: str) -> str:
        key = access_token_key(access_token)
        if cached := await cache.get(key):
            return cached

        jwt = validate_jwt(access_token, TokenTypes.ACCESS)  # type: ignore
        await AuthRepository.validate_access_token(access_token)  # type: ignore

        ttl = jwt.exp - int(time())
        if ttl > cls.MIN_CACHE_TTL:
            await cache.set(key, jwt.subject, ttl)

        return jwt.subject

    @staticmethod
    async def _delete_cached_access_tokens(*access_tokens: str) -> None:
        if access_tokens:
            keys = (access_token_key(access_token) for access_token in access_tokens)
            await cache.delete_many(*keys)
