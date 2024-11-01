from grpc import StatusCode
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from errors import UnauthenticatedError
from utils import compare_passwords

from .models import AccessToken, RefreshToken, User


class CRUD:
    @classmethod
    async def register(cls, data: dict[str, str], session: AsyncSession) -> str:
        async with session:
            try:
                new_user = User(**data)
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                return user.user_id
            except IntegrityError as exc:
                await session.rollback()
                exc.args = (StatusCode.ALREADY_EXISTS, "User already exists")
                raise exc
            except Exception as exc:
                await session.rollback()
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

    @classmethod
    async def verify_email(cls, user_id: str, session: AsyncSession) -> None:
        async with session:
            try:
                user = await session.get(User, user_id)

                if not user:
                    raise UnauthenticatedError(
                        StatusCode.UNAUTHENTICATED, "Invalid credentials"
                    )

                user.verified = True
                await session.commit()
            except Exception as exc:
                await session.rollback()
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

    @classmethod
    async def log_in(cls, data: dict[str, str], session: AsyncSession) -> None:
        async with session:
            try:
                new_access_token = AccessToken(
                    access_token=data.pop("access_token"),
                    refresh_token=data["refresh_token"],
                )
                new_refresh_token = RefreshToken(**data)

                session.add(new_access_token)
                session.add(new_refresh_token)
                await session.commit()
            except IntegrityError as exc:
                await session.rollback()
                exc.args = (StatusCode.ALREADY_EXISTS, "Token already exists")
                raise exc
            except Exception as exc:
                await session.rollback()
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

    @classmethod
    async def log_out(cls, access_token: str, session: AsyncSession) -> None:
        async with session:
            try:
                token = await session.get(AccessToken, access_token)
                await session.execute(
                    delete(RefreshToken).filter(
                        RefreshToken.refresh_token == token.refresh_token
                    )
                )
                await session.commit()
            except Exception as exc:
                await session.rollback()
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

    @classmethod
    async def refresh(cls, data: dict[str, str], session: AsyncSession) -> None:
        async with session:
            try:
                await session.execute(
                    delete(RefreshToken).filter(
                        RefreshToken.refresh_token == data["old_token"]
                    )
                )
                del data["old_token"]

                new_access_token = AccessToken(
                    access_token=data["access_token"],
                    refresh_token=data["refresh_token"],
                )
                del data["access_token"]
                new_refresh_token = RefreshToken(**data)
                session.add(new_access_token)
                session.add(new_refresh_token)
                await session.commit()
            except IntegrityError as exc:
                await session.rollback()
                exc.args = (StatusCode.ALREADY_EXISTS, "Refresh token already exists")
                raise exc
            except UnauthenticatedError as exc:
                await session.rollback()
                raise exc
            except Exception as exc:
                await session.rollback()
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

    @classmethod
    async def session_list(
        cls, user_id: str, session: AsyncSession
    ) -> tuple[dict[str, str]]:
        async with session:
            try:
                tokens = (
                    (
                        await session.execute(
                            select(RefreshToken).filter(RefreshToken.user_id == user_id)
                        )
                    )
                    .scalars()
                    .all()
                )
                result = tuple(token.columns_to_dict() for token in tokens)
                return result
            except Exception as exc:
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

    @classmethod
    async def revoke_session(cls, refresh_token_id: str, session: AsyncSession) -> None:
        async with session:
            try:
                await session.execute(
                    delete(RefreshToken).filter(
                        RefreshToken.token_id == refresh_token_id
                    )
                )
                await session.commit()
            except Exception as exc:
                await session.rollback()
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

    @classmethod
    async def validate_access_token(
        cls, access_token: str, session: AsyncSession
    ) -> bool:
        async with session:
            try:
                result = await session.get(AccessToken, access_token)
                return bool(result)
            except Exception as exc:
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

    @classmethod
    async def validate_refresh_token(
        cls, token_or_id: str, session: AsyncSession
    ) -> bool:
        async with session:
            try:
                if token_or_id.count(".") == 2:
                    result = (
                        await session.execute(
                            select(RefreshToken).filter(
                                RefreshToken.refresh_token == token_or_id
                            )
                        )
                    ).scalar_one_or_none()
                else:
                    result = await session.get(RefreshToken, token_or_id)

                return bool(result)
            except Exception as exc:
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

    @classmethod
    async def profile(
        cls, username_or_id: str, session: AsyncSession
    ) -> dict[str, str]:
        async with session:
            try:
                if len(username_or_id) == 36:
                    user = await session.get(User, username_or_id)
                else:
                    user = (
                        await session.execute(
                            select(User).filter(User.username == username_or_id)
                        )
                    ).scalar_one_or_none()

                if not user:
                    raise UnauthenticatedError(
                        StatusCode.UNAUTHENTICATED, "Invalid credentials"
                    )

                return user.columns_to_dict()
            except UnauthenticatedError as exc:
                raise exc
            except Exception as exc:
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

    @classmethod
    async def update_email(
        cls, data: dict[str, str], session: AsyncSession
    ) -> tuple[str, str]:
        async with session:
            try:
                user = await session.get(User, data["user_id"])

                if not user:
                    raise UnauthenticatedError(
                        StatusCode.UNAUTHENTICATED, "Invalid credentials"
                    )

                user.email = data["new_email"]
                user.verified = False
                data["username"] = user.username
                await session.commit()
                return data["username"], data["new_email"]
            except UnauthenticatedError as exc:
                await session.rollback()
                raise exc
            except IntegrityError as exc:
                await session.rollback()
                exc.args = (
                    StatusCode.ALREADY_EXISTS,
                    "Email address is already in use",
                )
                raise exc
            except Exception as exc:
                await session.rollback()
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

    @classmethod
    async def update_password(cls, data: dict[str, str], session: AsyncSession) -> None:
        async with session:
            try:
                user = await session.get(User, data["user_id"])

                if not user:
                    raise UnauthenticatedError(
                        StatusCode.UNAUTHENTICATED, "Invalid credentials"
                    )

                password_is_valid = compare_passwords(
                    data["old_password"], user.password
                )

                if not password_is_valid:
                    raise UnauthenticatedError(
                        StatusCode.UNAUTHENTICATED, "Invalid credentials"
                    )

                user.password = data["new_password"]
                await session.execute(
                    delete(RefreshToken).filter(RefreshToken.user_id == user.user_id)
                )
                await session.commit()
            except UnauthenticatedError as exc:
                await session.rollback()
                raise exc
            except Exception as exc:
                await session.rollback()
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

    @classmethod
    async def delete_profile(cls, user_id: str, session: AsyncSession) -> None:
        async with session:
            try:
                row_count = (
                    await session.execute(delete(User).filter(User.user_id == user_id))
                ).rowcount

                if row_count == 0:
                    raise UnauthenticatedError(
                        StatusCode.UNAUTHENTICATED, "Invalid credentials"
                    )
                await session.commit()
            except UnauthenticatedError as exc:
                await session.rollback()
                raise exc
            except Exception as exc:
                await session.rollback()
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc
