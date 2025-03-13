import re
from uuid import UUID

from grpc import StatusCode
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from dto import request as request_dto
from dto import response as response_dto
from errors import UnauthenticatedError
from utils import compare_passwords

from .models import TokenPair, User


class AuthRepository:
    _EMAIL_REGEX = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$")

    @classmethod
    async def register(
        cls, data: request_dto.RegisterRequestDTO, session: AsyncSession
    ) -> str:
        try:
            new_user = User(**data.dict())
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user.user_id
        except IntegrityError as exc:
            await session.rollback()
            exc.args = (StatusCode.ALREADY_EXISTS, "User already exists")
            raise exc
        except Exception as exc:
            await session.rollback()
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def verify_email(cls, user_id: str, session: AsyncSession) -> None:
        try:
            user = await session.get(User, user_id)

            if not user:
                raise UnauthenticatedError(
                    StatusCode.UNAUTHENTICATED, "Token is invalid"
                )

            user.verified = True
            await session.commit()
        except UnauthenticatedError as exc:
            await session.rollback()
            raise exc
        except Exception as exc:
            await session.rollback()
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def reset_password(
        cls, data: request_dto.ResetPasswordRequestDTO, session: AsyncSession
    ) -> None:
        try:
            user = await session.get(User, data.user_id)

            if not user:
                raise UnauthenticatedError(
                    StatusCode.UNAUTHENTICATED, "Invalid credentials"
                )

            user.password = data.new_password
            await session.execute(
                delete(TokenPair).filter(TokenPair.user_id == user.user_id)
            )
            await session.commit()
        except UnauthenticatedError as exc:
            await session.rollback()
            raise exc
        except Exception as exc:
            await session.rollback()
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def log_in(
        cls, data: request_dto.LogInDataRequestDTO, session: AsyncSession
    ) -> None:
        try:
            new_token_pair = TokenPair(
                user_id=data.user_id,
                access_token=data.access_token,
                refresh_token=data.refresh_token,
                user_ip=data.user_ip,
                browser=data.browser,
            )

            session.add(new_token_pair)
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            exc.args = (StatusCode.ALREADY_EXISTS, "Token already exists")
            raise exc
        except Exception as exc:
            await session.rollback()
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def log_out(cls, access_token: str, session: AsyncSession) -> None:
        try:
            token_pair = (
                await session.execute(
                    select(TokenPair).filter(TokenPair.access_token == access_token)
                )
            ).scalar_one_or_none()

            if not token_pair:
                raise UnauthenticatedError(
                    StatusCode.UNAUTHENTICATED, "Token is invalid"
                )

            await session.delete(token_pair)
            await session.commit()
        except UnauthenticatedError as exc:
            await session.rollback()
            raise exc
        except Exception as exc:
            await session.rollback()
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def refresh(
        cls, data: request_dto.RefreshDataRequestDTO, session: AsyncSession
    ) -> None:
        try:
            await session.execute(
                delete(TokenPair).filter(
                    TokenPair.refresh_token == data.old_refresh_token
                )
            )

            new_token_pair = TokenPair(
                user_id=data.user_id,
                access_token=data.access_token,
                refresh_token=data.refresh_token,
                user_ip=data.user_ip,
                browser=data.browser,
            )

            session.add(new_token_pair)
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            exc.args = (StatusCode.ALREADY_EXISTS, "Token already exists")
            raise exc
        except Exception as exc:
            await session.rollback()
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def session_list(
        cls, user_id: str, session: AsyncSession
    ) -> tuple[response_dto.SessionInfoResponseDTO, ...]:
        try:
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
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def revoke_session(cls, session_id: str, session: AsyncSession) -> None:
        try:
            await session.execute(
                delete(TokenPair).filter(TokenPair.session_id == session_id)
            )
            await session.commit()
        except Exception as exc:
            await session.rollback()
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def validate_access_token(
        cls, access_token: str, session: AsyncSession
    ) -> None:
        try:
            token_pair = (
                await session.execute(
                    select(TokenPair).filter(TokenPair.access_token == access_token)
                )
            ).scalar_one_or_none()

            if not token_pair:
                raise UnauthenticatedError(
                    StatusCode.UNAUTHENTICATED, "Token is invalid"
                )
        except UnauthenticatedError as exc:
            raise exc
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def validate_refresh_token(
        cls, token_or_id: str, session: AsyncSession
    ) -> None:
        try:
            if token_or_id.count(".") == 2:
                token_pair = (
                    await session.execute(
                        select(TokenPair).filter(TokenPair.refresh_token == token_or_id)
                    )
                ).scalar_one_or_none()
            else:
                token_pair = await session.get(TokenPair, token_or_id)

            if not token_pair:
                raise UnauthenticatedError(
                    StatusCode.UNAUTHENTICATED, "Token is invalid"
                )
        except UnauthenticatedError as exc:
            raise exc
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def profile(
        cls, username_email_id: str, session: AsyncSession
    ) -> response_dto.ProfileResponseDTO:
        try:
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
        except UnauthenticatedError as exc:
            raise exc
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def update_email(
        cls, data: request_dto.UpdateEmailDataRequestDTO, session: AsyncSession
    ) -> str:
        try:
            user = await session.get(User, data.user_id)

            if not user:
                raise UnauthenticatedError(
                    StatusCode.UNAUTHENTICATED, "Invalid credentials"
                )

            user.email = data.new_email
            user.verified = False
            await session.commit()
            await session.refresh(user)
            return user.username
        except UnauthenticatedError as exc:
            await session.rollback()
            raise exc
        except IntegrityError as exc:
            await session.rollback()
            exc.args = (StatusCode.ALREADY_EXISTS, "Email address is already in use")
            raise exc
        except Exception as exc:
            await session.rollback()
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def update_password(
        cls, data: request_dto.UpdatePasswordDataRequestDTO, session: AsyncSession
    ) -> None:
        try:
            user = await session.get(User, data.user_id)

            if not user:
                raise UnauthenticatedError(
                    StatusCode.UNAUTHENTICATED, "Invalid credentials"
                )

            compare_passwords(data.old_password, user.password)
            user.password = data.new_password
            await session.execute(
                delete(TokenPair).filter(TokenPair.user_id == user.user_id)
            )
            await session.commit()
        except UnauthenticatedError as exc:
            await session.rollback()
            raise exc
        except Exception as exc:
            await session.rollback()
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def delete_profile(cls, user_id: str, session: AsyncSession) -> None:
        try:
            row_count = (
                await session.execute(delete(User).filter(User.user_id == user_id))
            ).rowcount

            if not row_count:
                raise UnauthenticatedError(
                    StatusCode.UNAUTHENTICATED, "Invalid credentials"
                )
            await session.commit()
        except UnauthenticatedError as exc:
            await session.rollback()
            raise exc
        except Exception as exc:
            await session.rollback()
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc
