from uuid import UUID

from grpc import StatusCode
from sqlalchemy import delete, select, true
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from dto import request as request_dto
from dto import response as response_dto
from exceptions import SessionNotFoundException, UnauthenticatedException
from utils import EMAIL_REGEX, compare_passwords, with_transaction

from .models import TokenPair, User


class AuthRepository:
    @staticmethod
    @with_transaction
    async def register(
        data: request_dto.RegisterRequestDTO, session: AsyncSession
    ) -> str:
        new_user = data.to_model(User)
        session.add(new_user)

        try:
            await session.commit()
        except IntegrityError as exc:
            exc.args = (StatusCode.ALREADY_EXISTS, "User already exists")
            raise exc

        await session.refresh(new_user)
        return new_user.user_id

    @classmethod
    @with_transaction
    async def confirm_email(cls, user_id: str, session: AsyncSession) -> None:
        user = await cls._get_user(user_id, session)
        user.email_confirmed = True
        await session.commit()

    @classmethod
    @with_transaction
    async def reset_password(
        cls, data: request_dto.ResetPasswordRequestDTO, session: AsyncSession
    ) -> list[str]:
        user = await cls._get_user(data.user_id, session)
        user.password = data.new_password
        deleted_access_tokens = list(
            await session.scalars(
                delete(TokenPair)
                .filter(TokenPair.user_id == user.user_id)
                .returning(TokenPair.access_token)
            )
        )
        await session.commit()
        return deleted_access_tokens

    @staticmethod
    @with_transaction
    async def log_in(
        data: request_dto.LogInDataRequestDTO, session: AsyncSession
    ) -> None:
        new_token_pair = data.to_model(TokenPair)
        session.add(new_token_pair)

        try:
            await session.commit()
        except IntegrityError as exc:
            exc.args = (StatusCode.ALREADY_EXISTS, "Token already exists")
            raise exc

    @staticmethod
    @with_transaction
    async def log_out(access_token: str, session: AsyncSession) -> None:
        token_pair = (
            await session.execute(
                select(TokenPair).filter(TokenPair.access_token == access_token)
            )
        ).scalar_one_or_none()

        if not token_pair:
            raise UnauthenticatedException("Token is invalid")

        await session.delete(token_pair)
        await session.commit()

    @staticmethod
    @with_transaction
    async def refresh(
        data: request_dto.RefreshDataRequestDTO, session: AsyncSession
    ) -> str:
        deleted_access_token = (
            await session.execute(
                delete(TokenPair)
                .filter(TokenPair.refresh_token == data.old_refresh_token)
                .returning(TokenPair.access_token)
            )
        ).scalar_one_or_none()

        if not deleted_access_token:
            raise UnauthenticatedException("Token is invalid")

        new_token_pair = data.to_model(TokenPair)
        session.add(new_token_pair)

        try:
            await session.commit()
        except IntegrityError as exc:
            exc.args = (StatusCode.ALREADY_EXISTS, "Token already exists")
            raise exc
        return deleted_access_token

    @staticmethod
    @with_transaction
    async def session_list(
        user_id: str, session: AsyncSession
    ) -> list[response_dto.SessionInfoResponseDTO]:
        token_pairs = await session.scalars(
            select(TokenPair)
            .filter(TokenPair.user_id == user_id)
            .order_by(TokenPair.created_at.desc())
        )
        return [
            response_dto.SessionInfoResponseDTO.from_model(token_pair)
            for token_pair in token_pairs
        ]

    @staticmethod
    @with_transaction
    async def revoke_session(session_id: str, session: AsyncSession) -> str:
        deleted_access_token = (
            await session.execute(
                delete(TokenPair)
                .filter(TokenPair.session_id == session_id)
                .returning(TokenPair.access_token)
            )
        ).scalar_one_or_none()

        if not deleted_access_token:
            raise SessionNotFoundException

        await session.commit()
        return deleted_access_token

    @staticmethod
    @with_transaction
    async def validate_access_token(access_token: str, session: AsyncSession) -> None:
        token_pair = (
            await session.execute(
                select(TokenPair).filter(TokenPair.access_token == access_token)
            )
        ).scalar_one_or_none()

        if not token_pair:
            raise UnauthenticatedException("Token is invalid")

    @staticmethod
    @with_transaction
    async def profile(
        username_email_id: str, session: AsyncSession
    ) -> response_dto.ProfileResponseDTO:
        try:
            UUID(username_email_id)
            user = await session.get(User, username_email_id)
        except ValueError:
            if EMAIL_REGEX.fullmatch(username_email_id):
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
            raise UnauthenticatedException("Invalid credentials")
        return response_dto.ProfileResponseDTO.from_model(user)

    @classmethod
    @with_transaction
    async def update_email(
        cls, data: request_dto.UpdateEmailDataRequestDTO, session: AsyncSession
    ) -> str:
        user = await cls._get_user(data.user_id, session)
        user.email = data.new_email
        user.email_confirmed = False

        try:
            await session.commit()
        except IntegrityError as exc:
            exc.args = (StatusCode.ALREADY_EXISTS, "Email address is already in use")
            raise exc
        return user.username

    @classmethod
    @with_transaction
    async def update_password(
        cls, data: request_dto.UpdatePasswordDataRequestDTO, session: AsyncSession
    ) -> list[str]:
        user = await cls._get_user(data.user_id, session)
        compare_passwords(data.old_password, user.password)
        user.password = data.new_password

        deleted_access_tokens = list(
            await session.scalars(
                delete(TokenPair)
                .filter(TokenPair.user_id == user.user_id)
                .returning(TokenPair.access_token)
            )
        )
        await session.commit()
        return deleted_access_tokens

    @staticmethod
    @with_transaction
    async def delete_profile(user_id: str, session: AsyncSession) -> list[str]:
        tokens_cte = (
            delete(TokenPair)
            .where(TokenPair.user_id == user_id)
            .returning(TokenPair.access_token)
            .cte("deleted_tokens")
        )
        user_cte = (
            delete(User)
            .where(User.user_id == user_id)
            .returning(User.user_id)
            .cte("deleted_user")
        )
        stmt = select(user_cte.c.user_id, tokens_cte.c.access_token).select_from(
            user_cte.outerjoin(tokens_cte, true())
        )
        result = await session.execute(stmt)
        rows = result.all()

        if not rows:
            raise UnauthenticatedException("Invalid credentials")

        deleted_access_tokens = [r[1] for r in rows if r[1] is not None]
        await session.commit()
        return deleted_access_tokens

    @staticmethod
    async def _get_user(user_id: str, session: AsyncSession) -> User:
        user = await session.get(User, user_id)
        if not user:
            raise UnauthenticatedException("Invalid credentials")
        return user
