from cashews import cache
from grpc import StatusCode

from dto import request as request_dto
from dto import response as response_dto
from enums import TokenTypes
from exceptions import UnauthenticatedException
from repository import AuthRepository
from utils import (
    compare_passwords,
    convert_user_agent,
    generate_jwt,
    generate_reset_code,
    get_hashed_password,
    validate_jwt,
)


class AuthService:
    @staticmethod
    async def register(
        data: request_dto.RegisterRequestDTO,
    ) -> str:
        data = data.replace(password=get_hashed_password(data.password))
        user_id = await AuthRepository.register(data)  # type: ignore
        return generate_jwt(user_id, TokenTypes.VERIFICATION)  # type: ignore

    @staticmethod
    async def verify_email(verification_token: str) -> None:
        user_id = validate_jwt(verification_token, TokenTypes.VERIFICATION)  # type: ignore
        await AuthRepository.verify_email(user_id)  # type: ignore
        await cache.delete_many(f"auth-{user_id}", f"profile-{user_id}")

    @staticmethod
    async def request_reset_code(email: str) -> response_dto.ResetCodeResponseDTO:
        profile = await AuthRepository.profile(email)  # type: ignore
        code = generate_reset_code()
        await cache.set(f"reset-{profile.user_id}", code, 600)
        return response_dto.ResetCodeResponseDTO(
            profile.user_id, profile.username, code
        )

    @staticmethod
    async def validate_reset_code(data: request_dto.ResetCodeRequestDTO) -> bool:
        code = await cache.get(f"reset-{data.user_id}")

        if not code or data.code != code:
            return False

        await cache.set(f"reset-{data.user_id}", "validated", 600)
        return True

    @staticmethod
    async def reset_password(data: request_dto.ResetPasswordRequestDTO) -> None:
        code = await cache.get(f"reset-{data.user_id}")

        if not code or code != "validated":
            raise UnauthenticatedException(
                StatusCode.UNAUTHENTICATED, "Code is not validated"
            )

        data = data.replace(new_password=get_hashed_password(data.new_password))
        await AuthRepository.reset_password(data)  # type: ignore
        await cache.delete(f"reset-{data.user_id}")

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
        await cache.delete(f"session_list-{profile.user_id}")
        return response_dto.LogInResponseDTO(
            access_token, refresh_token, profile.email, browser, profile.verified
        )

    @staticmethod
    async def log_out(access_token: str) -> None:
        user_id = validate_jwt(access_token, TokenTypes.ACCESS)  # type: ignore
        await AuthRepository.validate_access_token(access_token)  # type: ignore
        await AuthRepository.log_out(access_token)  # type: ignore
        await cache.delete(f"session_list-{user_id}")

    @staticmethod
    async def resend_verification_mail(
        access_token: str,
    ) -> response_dto.VerificationMailResponseDTO:
        user_id = validate_jwt(access_token, TokenTypes.ACCESS)  # type: ignore
        await AuthRepository.validate_access_token(access_token)  # type: ignore

        profile = await AuthRepository.profile(user_id)  # type: ignore
        verification_token = generate_jwt(user_id, TokenTypes.VERIFICATION)  # type: ignore
        return response_dto.VerificationMailResponseDTO(
            verification_token, profile.username, profile.email
        )

    @staticmethod
    async def auth(access_token: str) -> str:
        user_id = validate_jwt(access_token, TokenTypes.ACCESS)  # type: ignore
        await AuthRepository.validate_access_token(access_token)  # type: ignore
        return user_id

    @staticmethod
    async def refresh(
        data: request_dto.RefreshRequestDTO,
    ) -> response_dto.RefreshResponseDTO:
        user_id = validate_jwt(data.refresh_token, TokenTypes.REFRESH)  # type: ignore
        await AuthRepository.validate_refresh_token(data.refresh_token)  # type: ignore

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

        await AuthRepository.refresh(dto)  # type: ignore
        await cache.delete(f"session_list-{user_id}")
        return response_dto.RefreshResponseDTO(access_token, refresh_token)

    @staticmethod
    async def session_list(
        access_token: str,
    ) -> tuple[response_dto.SessionInfoResponseDTO, ...]:
        user_id = validate_jwt(access_token, TokenTypes.ACCESS)  # type: ignore
        await AuthRepository.validate_access_token(access_token)  # type: ignore

        if cached := await cache.get(f"session_list-{user_id}"):
            return cached

        sessions = await AuthRepository.session_list(user_id)  # type: ignore
        await cache.set(f"session_list-{user_id}", sessions, 3600)
        return sessions

    @staticmethod
    async def revoke_session(data: request_dto.RevokeSessionRequestDTO) -> None:
        user_id = validate_jwt(data.access_token, TokenTypes.ACCESS)  # type: ignore
        await AuthRepository.validate_access_token(data.access_token)  # type: ignore
        await AuthRepository.validate_refresh_token(data.session_id)  # type: ignore
        await AuthRepository.revoke_session(data.session_id)  # type: ignore
        await cache.delete(f"session_list-{user_id}")

    @staticmethod
    async def profile(access_token: str) -> response_dto.ProfileResponseDTO:
        user_id = validate_jwt(access_token, TokenTypes.ACCESS)  # type: ignore
        await AuthRepository.validate_access_token(access_token)  # type: ignore

        if cached := await cache.get(f"profile-{user_id}"):
            return cached

        profile = await AuthRepository.profile(user_id)  # type: ignore
        await cache.set(f"profile-{user_id}", profile, 3600)
        return profile

    @staticmethod
    async def update_email(
        data: request_dto.UpdateEmailRequestDTO,
    ) -> response_dto.VerificationMailResponseDTO:
        user_id = validate_jwt(data.access_token, TokenTypes.ACCESS)  # type: ignore
        await AuthRepository.validate_access_token(data.access_token)  # type: ignore

        dto = request_dto.UpdateEmailDataRequestDTO(
            user_id, data.access_token, data.new_email
        )

        username = await AuthRepository.update_email(dto)  # type: ignore
        await cache.delete_many(f"auth-{user_id}", f"profile-{user_id}")
        verification_token = generate_jwt(user_id, TokenTypes.VERIFICATION)  # type: ignore
        return response_dto.VerificationMailResponseDTO(
            verification_token, username, data.new_email
        )

    @staticmethod
    async def update_password(data: request_dto.UpdatePasswordRequestDTO) -> None:
        user_id = validate_jwt(data.access_token, TokenTypes.ACCESS)  # type: ignore
        await AuthRepository.validate_access_token(data.access_token)  # type: ignore

        dto = request_dto.UpdatePasswordDataRequestDTO(
            user_id,
            data.access_token,
            data.old_password,
            get_hashed_password(data.new_password),
        )
        await AuthRepository.update_password(dto)  # type: ignore

    @staticmethod
    async def delete_profile(access_token: str) -> str:
        user_id = validate_jwt(access_token, TokenTypes.ACCESS)  # type: ignore
        await AuthRepository.validate_access_token(access_token)  # type: ignore
        await AuthRepository.delete_profile(user_id)  # type: ignore
        await cache.delete_match(rf"\w+-{user_id}")
        return user_id
