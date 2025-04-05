from cashews import cache
from grpc import StatusCode
from sqlalchemy.ext.asyncio import AsyncSession

from dto import request as request_dto
from dto import response as response_dto
from exceptions import UnauthenticatedException
from repository import AuthRepository, get_session
from utils import (
    TokenTypes,
    compare_passwords,
    convert_user_agent,
    generate_jwt,
    generate_reset_code,
    get_hashed_password,
    validate_jwt,
)


class AuthService:
    @classmethod
    @get_session
    async def register(
        cls, data: request_dto.RegisterRequestDTO, *, session: AsyncSession
    ) -> response_dto.VerificationMailResponseDTO:
        data = data.replace(password=get_hashed_password(data.password))
        user_id = await AuthRepository.register(data, session=session)
        verification_token = generate_jwt(user_id, TokenTypes.VERIFICATION)
        return response_dto.VerificationMailResponseDTO(
            verification_token, data.username, data.email
        )

    @classmethod
    @get_session
    async def verify_email(
        cls, verification_token: str, *, session: AsyncSession
    ) -> None:
        user_id = validate_jwt(verification_token, TokenTypes.VERIFICATION)
        await AuthRepository.verify_email(user_id, session=session)
        await cache.delete_many(f"auth-{user_id}", f"profile-{user_id}")

    @classmethod
    @get_session
    async def request_reset_code(
        cls, email: str, *, session: AsyncSession
    ) -> response_dto.ResetCodeResponseDTO:
        profile = await AuthRepository.profile(email, session=session)
        code = generate_reset_code()
        await cache.set(f"reset-{profile.user_id}", code, 600)
        return response_dto.ResetCodeResponseDTO(
            profile.user_id, profile.username, code
        )

    @classmethod
    async def validate_reset_code(cls, data: request_dto.ResetCodeRequestDTO) -> bool:
        code = await cache.get(f"reset-{data.user_id}")

        if not code or data.code != code:
            return False

        await cache.set(f"reset-{data.user_id}", "validated", 600)
        return True

    @classmethod
    @get_session
    async def reset_password(
        cls, data: request_dto.ResetPasswordRequestDTO, *, session: AsyncSession
    ) -> None:
        code = await cache.get(f"reset-{data.user_id}")

        if not code or code != "validated":
            raise UnauthenticatedException(
                StatusCode.UNAUTHENTICATED, "Code is not validated"
            )

        data = data.replace(new_password=get_hashed_password(data.new_password))
        await AuthRepository.reset_password(data, session=session)
        await cache.delete(f"reset-{data.user_id}")

    @classmethod
    @get_session
    async def log_in(
        cls, data: request_dto.LogInRequestDTO, *, session: AsyncSession
    ) -> response_dto.LogInResponseDTO:
        profile = await AuthRepository.profile(data.username, session=session)
        compare_passwords(data.password, profile.password)  # type: ignore

        access_token = generate_jwt(profile.user_id, TokenTypes.ACCESS)
        refresh_token = generate_jwt(profile.user_id, TokenTypes.REFRESH)
        browser = convert_user_agent(data.user_agent)

        dto = request_dto.LogInDataRequestDTO(
            access_token, refresh_token, profile.user_id, data.user_ip, browser
        )

        await AuthRepository.log_in(dto, session=session)
        await cache.delete(f"session_list-{profile.user_id}")
        return response_dto.LogInResponseDTO(
            access_token, refresh_token, profile.email, browser, profile.verified
        )

    @classmethod
    @get_session
    async def log_out(cls, access_token: str, *, session: AsyncSession) -> None:
        user_id = validate_jwt(access_token, TokenTypes.ACCESS)
        await AuthRepository.validate_access_token(access_token, session=session)
        await AuthRepository.log_out(access_token, session=session)
        await cache.delete(f"session_list-{user_id}")

    @classmethod
    @get_session
    async def resend_verification_mail(
        cls, access_token: str, *, session: AsyncSession
    ) -> response_dto.VerificationMailResponseDTO:
        user_id = validate_jwt(access_token, TokenTypes.ACCESS)
        await AuthRepository.validate_access_token(access_token, session=session)

        profile = await AuthRepository.profile(user_id, session=session)
        verification_token = generate_jwt(user_id, TokenTypes.VERIFICATION)
        return response_dto.VerificationMailResponseDTO(
            verification_token, profile.username, profile.email
        )

    @classmethod
    @get_session
    async def auth(cls, access_token: str, *, session: AsyncSession) -> str:
        user_id = validate_jwt(access_token, TokenTypes.ACCESS)
        await AuthRepository.validate_access_token(access_token, session=session)
        return user_id

    @classmethod
    @get_session
    async def refresh(
        cls, data: request_dto.RefreshRequestDTO, *, session: AsyncSession
    ) -> response_dto.RefreshResponseDTO:
        user_id = validate_jwt(data.refresh_token, TokenTypes.REFRESH)
        await AuthRepository.validate_refresh_token(data.refresh_token, session=session)

        access_token = generate_jwt(user_id, TokenTypes.ACCESS)
        refresh_token = generate_jwt(user_id, TokenTypes.REFRESH)
        browser = convert_user_agent(data.user_agent)

        dto = request_dto.RefreshDataRequestDTO(
            access_token,
            refresh_token,
            data.refresh_token,
            user_id,
            data.user_ip,
            browser,
        )

        await AuthRepository.refresh(dto, session=session)
        await cache.delete(f"session_list-{user_id}")
        tokens = response_dto.RefreshResponseDTO(access_token, refresh_token)
        return tokens

    @classmethod
    @get_session
    async def session_list(
        cls, access_token: str, *, session: AsyncSession
    ) -> tuple[response_dto.SessionInfoResponseDTO, ...]:
        user_id = validate_jwt(access_token, TokenTypes.ACCESS)
        await AuthRepository.validate_access_token(access_token, session=session)

        if cached := await cache.get(f"session_list-{user_id}"):
            return cached

        sessions = await AuthRepository.session_list(user_id, session=session)
        sessions = tuple(
            session.replace(user_id=None, access_token=None, refresh_token=None)
            for session in sessions
        )
        await cache.set(f"session_list-{user_id}", sessions, 3600)
        return sessions

    @classmethod
    @get_session
    async def revoke_session(
        cls, data: request_dto.RevokeSessionRequestDTO, *, session: AsyncSession
    ) -> None:
        user_id = validate_jwt(data.access_token, TokenTypes.ACCESS)
        await AuthRepository.validate_access_token(data.access_token, session=session)
        await AuthRepository.validate_refresh_token(data.session_id, session=session)
        await AuthRepository.revoke_session(data.session_id, session=session)
        await cache.delete(f"session_list-{user_id}")

    @classmethod
    @get_session
    async def profile(
        cls, access_token: str, *, session: AsyncSession
    ) -> response_dto.ProfileResponseDTO:
        user_id = validate_jwt(access_token, TokenTypes.ACCESS)
        await AuthRepository.validate_access_token(access_token, session=session)

        if cached := await cache.get(f"profile-{user_id}"):
            return cached

        profile = await AuthRepository.profile(user_id, session=session)
        profile = profile.replace(password=None)
        await cache.set(f"profile-{user_id}", profile, 3600)
        return profile

    @classmethod
    @get_session
    async def update_email(
        cls, data: request_dto.UpdateEmailRequestDTO, *, session: AsyncSession
    ) -> response_dto.VerificationMailResponseDTO:
        user_id = validate_jwt(data.access_token, TokenTypes.ACCESS)
        await AuthRepository.validate_access_token(data.access_token, session=session)

        dto = request_dto.UpdateEmailDataRequestDTO(
            user_id, data.access_token, data.new_email
        )

        username = await AuthRepository.update_email(dto, session=session)
        await cache.delete_many(f"auth-{user_id}", f"profile-{user_id}")
        verification_token = generate_jwt(user_id, TokenTypes.VERIFICATION)
        return response_dto.VerificationMailResponseDTO(
            verification_token, username, data.new_email
        )

    @classmethod
    @get_session
    async def update_password(
        cls, data: request_dto.UpdatePasswordRequestDTO, *, session: AsyncSession
    ) -> None:
        user_id = validate_jwt(data.access_token, TokenTypes.ACCESS)
        await AuthRepository.validate_access_token(data.access_token, session=session)

        dto = request_dto.UpdatePasswordDataRequestDTO(
            user_id,
            data.access_token,
            data.old_password,
            get_hashed_password(data.new_password),
        )
        await AuthRepository.update_password(dto, session=session)

    @classmethod
    @get_session
    async def delete_profile(cls, access_token: str, *, session: AsyncSession) -> str:
        user_id = validate_jwt(access_token, TokenTypes.ACCESS)
        await AuthRepository.validate_access_token(access_token, session=session)
        await AuthRepository.delete_profile(user_id, session=session)
        await cache.delete_match(rf"\w+-{user_id}")
        return user_id
