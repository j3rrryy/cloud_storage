from typing import cast

from sqlalchemy import CursorResult, delete, exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from dto import request as request_dto
from dto import response as response_dto
from exceptions import (
    EmailAddressIsAlreadyInUseException,
    SessionNotFoundException,
    TokenAlreadyExistsException,
    UnauthenticatedException,
    UserAlreadyExistsException,
)
from protocols import AuthRepositoryProtocol
from utils import database_exception_handler

from .models import TokenPair, User


class AuthRepository(AuthRepositoryProtocol):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self._sessionmaker = sessionmaker

    @database_exception_handler
    async def register(self, data: request_dto.RegisterRequestDTO) -> str:
        new_user = data.to_model(User)
        try:
            async with self._sessionmaker.begin() as session:
                session.add(new_user)
                await session.flush()
        except IntegrityError:
            raise UserAlreadyExistsException
        return new_user.user_id

    @database_exception_handler
    async def confirm_email(self, user_id: str) -> None:
        async with self._sessionmaker.begin() as session:
            user = await self._get_user(user_id, session)
            user.email_confirmed = True

    @database_exception_handler
    async def reset_password(
        self, data: request_dto.ResetPasswordRequestDTO
    ) -> list[str]:
        async with self._sessionmaker.begin() as session:
            user = await self._get_user(data.user_id, session)
            user.password = data.new_password
            deleted_access_tokens = list(
                await session.scalars(
                    delete(TokenPair)
                    .where(TokenPair.user_id == user.user_id)
                    .returning(TokenPair.access_token)
                )
            )
        return deleted_access_tokens

    @database_exception_handler
    async def log_in(self, data: request_dto.LogInDataRequestDTO) -> None:
        new_token_pair = data.to_model(TokenPair)
        try:
            async with self._sessionmaker.begin() as session:
                session.add(new_token_pair)
        except IntegrityError:
            raise TokenAlreadyExistsException

    @database_exception_handler
    async def log_out(self, access_token: str) -> None:
        async with self._sessionmaker.begin() as session:
            result = await session.execute(
                delete(TokenPair).where(TokenPair.access_token == access_token)
            )
            result = cast(CursorResult, result)
            if not (result.rowcount or 0):
                raise UnauthenticatedException("Token is invalid")

    @database_exception_handler
    async def refresh(self, data: request_dto.RefreshDataRequestDTO) -> str:
        new_token_pair = data.to_model(TokenPair)
        try:
            async with self._sessionmaker.begin() as session:
                deleted_access_token = (
                    await session.execute(
                        delete(TokenPair)
                        .where(TokenPair.refresh_token == data.old_refresh_token)
                        .returning(TokenPair.access_token)
                    )
                ).scalar_one_or_none()

                if not deleted_access_token:
                    raise UnauthenticatedException("Token is invalid")

                session.add(new_token_pair)
        except IntegrityError:
            raise TokenAlreadyExistsException
        return deleted_access_token

    @database_exception_handler
    async def session_list(
        self, user_id: str
    ) -> list[response_dto.SessionInfoResponseDTO]:
        async with self._sessionmaker() as session:
            token_pairs = await session.scalars(
                select(TokenPair)
                .where(TokenPair.user_id == user_id)
                .order_by(TokenPair.created_at.desc())
            )
        return [
            response_dto.SessionInfoResponseDTO.from_model(token_pair)
            for token_pair in token_pairs
        ]

    @database_exception_handler
    async def revoke_session(self, session_id: str) -> str:
        async with self._sessionmaker.begin() as session:
            deleted_access_token = (
                await session.execute(
                    delete(TokenPair)
                    .where(TokenPair.session_id == session_id)
                    .returning(TokenPair.access_token)
                )
            ).scalar_one_or_none()
            if not deleted_access_token:
                raise SessionNotFoundException
        return deleted_access_token

    @database_exception_handler
    async def validate_access_token(self, access_token: str) -> None:
        async with self._sessionmaker() as session:
            result = await session.execute(
                select(exists().where(TokenPair.access_token == access_token))
            )
        if not result.scalar():
            raise UnauthenticatedException("Token is invalid")

    @database_exception_handler
    async def profile_by_user_id(self, user_id: str) -> response_dto.ProfileResponseDTO:
        async with self._sessionmaker() as session:
            user = await self._get_user(user_id, session)
        return response_dto.ProfileResponseDTO.from_model(user)

    @database_exception_handler
    async def profile_by_username(
        self, username: str
    ) -> response_dto.ProfileResponseDTO:
        async with self._sessionmaker() as session:
            user = (
                await session.execute(select(User).where(User.username == username))
            ).scalar_one_or_none()
        if not user:
            raise UnauthenticatedException("Invalid credentials")
        return response_dto.ProfileResponseDTO.from_model(user)

    @database_exception_handler
    async def profile_by_email(self, email: str) -> response_dto.ProfileResponseDTO:
        async with self._sessionmaker() as session:
            user = (
                await session.execute(select(User).where(User.email == email))
            ).scalar_one_or_none()
        if not user:
            raise UnauthenticatedException("Invalid credentials")
        return response_dto.ProfileResponseDTO.from_model(user)

    @database_exception_handler
    async def update_email(self, data: request_dto.UpdateEmailDataRequestDTO) -> str:
        try:
            async with self._sessionmaker.begin() as session:
                user = await self._get_user(data.user_id, session)
                user.email = data.new_email
                user.email_confirmed = False
        except IntegrityError:
            raise EmailAddressIsAlreadyInUseException
        return user.username

    @database_exception_handler
    async def update_password(
        self, data: request_dto.UpdatePasswordDataRequestDTO
    ) -> list[str]:
        async with self._sessionmaker.begin() as session:
            user = await self._get_user(data.user_id, session)
            user.password = data.new_password
            deleted_access_tokens = list(
                await session.scalars(
                    delete(TokenPair)
                    .where(TokenPair.user_id == user.user_id)
                    .returning(TokenPair.access_token)
                )
            )
        return deleted_access_tokens

    @database_exception_handler
    async def delete_profile(self, user_id: str) -> list[str]:
        async with self._sessionmaker.begin() as session:
            deleted_access_tokens = list(
                await session.scalars(
                    delete(TokenPair)
                    .where(TokenPair.user_id == user_id)
                    .returning(TokenPair.access_token)
                )
            )
            result = await session.execute(delete(User).where(User.user_id == user_id))
            result = cast(CursorResult, result)
            if not (result.rowcount or 0):
                raise UnauthenticatedException("Invalid credentials")

        return deleted_access_tokens

    async def _get_user(self, user_id: str, session: AsyncSession) -> User:
        if not (user := await session.get(User, user_id)):
            raise UnauthenticatedException("Invalid credentials")
        return user
