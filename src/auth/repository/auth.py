import re
from uuid import UUID

from grpc import StatusCode
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from dto import request as request_dto
from dto import response as response_dto
from errors import UnauthenticatedError
from utils import compare_passwords, repository_exception_handler

from .models import TokenPair, User


class AuthRepository:
    _EMAIL_REGEX = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$")

    @classmethod
    @repository_exception_handler
    async def register(
        cls, data: request_dto.RegisterRequestDTO, *, session: AsyncSession
    ) -> str:
        new_user = User(**data.dict())
        session.add(new_user)

        try:
            await session.commit()
        except IntegrityError as exc:
            exc.args = (StatusCode.ALREADY_EXISTS, "User already exists")
            raise exc

        await session.refresh(new_user)
        return new_user.user_id

    @classmethod
    @repository_exception_handler
    async def verify_email(cls, user_id: str, *, session: AsyncSession) -> None:
        if not (user := await session.get(User, user_id)):
            raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Token is invalid")

        user.verified = True
        await session.commit()

    @classmethod
    @repository_exception_handler
    async def reset_password(
        cls, data: request_dto.ResetPasswordRequestDTO, *, session: AsyncSession
    ) -> None:
        if not (user := await session.get(User, data.user_id)):
            raise UnauthenticatedError(
                StatusCode.UNAUTHENTICATED, "Invalid credentials"
            )

        user.password = data.new_password
        await session.execute(
            delete(TokenPair).filter(TokenPair.user_id == user.user_id)
        )
        await session.commit()

    @classmethod
    @repository_exception_handler
    async def log_in(
        cls, data: request_dto.LogInDataRequestDTO, *, session: AsyncSession
    ) -> None:
        new_token_pair = TokenPair(
            user_id=data.user_id,
            access_token=data.access_token,
            refresh_token=data.refresh_token,
            user_ip=data.user_ip,
            browser=data.browser,
        )
        session.add(new_token_pair)

        try:
            await session.commit()
        except IntegrityError as exc:
            exc.args = (StatusCode.ALREADY_EXISTS, "Token already exists")
            raise exc

    @classmethod
    @repository_exception_handler
    async def log_out(cls, access_token: str, *, session: AsyncSession) -> None:
        token_pair = (
            await session.execute(
                select(TokenPair).filter(TokenPair.access_token == access_token)
            )
        ).scalar_one_or_none()

        if not token_pair:
            raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Token is invalid")

        await session.delete(token_pair)
        await session.commit()

    @classmethod
    @repository_exception_handler
    async def refresh(
        cls, data: request_dto.RefreshDataRequestDTO, *, session: AsyncSession
    ) -> None:
        await session.execute(
            delete(TokenPair).filter(TokenPair.refresh_token == data.old_refresh_token)
        )
        new_token_pair = TokenPair(
            user_id=data.user_id,
            access_token=data.access_token,
            refresh_token=data.refresh_token,
            user_ip=data.user_ip,
            browser=data.browser,
        )
        session.add(new_token_pair)

        try:
            await session.commit()
        except IntegrityError as exc:
            exc.args = (StatusCode.ALREADY_EXISTS, "Token already exists")
            raise exc

    @classmethod
    @repository_exception_handler
    async def session_list(
        cls, user_id: str, *, session: AsyncSession
    ) -> tuple[response_dto.SessionInfoResponseDTO, ...]:
        token_pairs = (
            (
                await session.execute(
                    select(TokenPair).filter(TokenPair.user_id == user_id)
                )
            )
            .scalars()
            .all()
        )
        return tuple(
            response_dto.SessionInfoResponseDTO.from_model(token_pair)
            for token_pair in token_pairs
        )

    @classmethod
    @repository_exception_handler
    async def revoke_session(cls, session_id: str, *, session: AsyncSession) -> None:
        await session.execute(
            delete(TokenPair).filter(TokenPair.session_id == session_id)
        )
        await session.commit()

    @classmethod
    @repository_exception_handler
    async def validate_access_token(
        cls, access_token: str, *, session: AsyncSession
    ) -> None:
        token_pair = (
            await session.execute(
                select(TokenPair).filter(TokenPair.access_token == access_token)
            )
        ).scalar_one_or_none()

        if not token_pair:
            raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Token is invalid")

    @classmethod
    @repository_exception_handler
    async def validate_refresh_token(
        cls, token_or_id: str, *, session: AsyncSession
    ) -> None:
        if token_or_id.count(".") == 2:
            token_pair = (
                await session.execute(
                    select(TokenPair).filter(TokenPair.refresh_token == token_or_id)
                )
            ).scalar_one_or_none()
        else:
            token_pair = await session.get(TokenPair, token_or_id)

        if not token_pair:
            raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Token is invalid")

    @classmethod
    @repository_exception_handler
    async def profile(
        cls, username_email_id: str, *, session: AsyncSession
    ) -> response_dto.ProfileResponseDTO:
        try:
            UUID(username_email_id)
            user = await session.get(User, username_email_id)
        except ValueError:
            if cls._EMAIL_REGEX.fullmatch(username_email_id):
                user = (
                    await session.execute(
                        select(User).filter(User.email == username_email_id)
                    )
                ).scalar_one_or_none()
            else:
                user = (
                    await session.execute(
                        select(User).filter(User.username == username_email_id)
                    )
                ).scalar_one_or_none()

        if not user:
            raise UnauthenticatedError(
                StatusCode.UNAUTHENTICATED, "Invalid credentials"
            )
        return response_dto.ProfileResponseDTO.from_model(user)

    @classmethod
    @repository_exception_handler
    async def update_email(
        cls, data: request_dto.UpdateEmailDataRequestDTO, *, session: AsyncSession
    ) -> str:
        if not (user := await session.get(User, data.user_id)):
            raise UnauthenticatedError(
                StatusCode.UNAUTHENTICATED, "Invalid credentials"
            )

        user.email = data.new_email
        user.verified = False

        try:
            await session.commit()
        except IntegrityError as exc:
            exc.args = (StatusCode.ALREADY_EXISTS, "Email address is already in use")
            raise exc

        await session.refresh(user)
        return user.username

    @classmethod
    @repository_exception_handler
    async def update_password(
        cls, data: request_dto.UpdatePasswordDataRequestDTO, *, session: AsyncSession
    ) -> None:
        if not (user := await session.get(User, data.user_id)):
            raise UnauthenticatedError(
                StatusCode.UNAUTHENTICATED, "Invalid credentials"
            )

        compare_passwords(data.old_password, user.password)
        user.password = data.new_password
        await session.execute(
            delete(TokenPair).filter(TokenPair.user_id == user.user_id)
        )
        await session.commit()

    @classmethod
    @repository_exception_handler
    async def delete_profile(cls, user_id: str, *, session: AsyncSession) -> None:
        row_count = (
            await session.execute(delete(User).filter(User.user_id == user_id))
        ).rowcount

        if not row_count:
            raise UnauthenticatedError(
                StatusCode.UNAUTHENTICATED, "Invalid credentials"
            )
        await session.commit()
