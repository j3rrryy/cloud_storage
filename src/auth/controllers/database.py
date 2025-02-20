from cashews import cache
from grpc import StatusCode
from sqlalchemy.ext.asyncio import AsyncSession

from config import load_config
from database import CRUD, get_session
from errors import UnauthenticatedError
from utils import (
    TokenTypes,
    compare_passwords,
    generate_jwt,
    generate_reset_code,
    get_hashed_password,
    validate_jwt,
)
from utils.utils import convert_user_agent


class DatabaseController:
    _config = load_config()

    @classmethod
    @get_session
    async def register(
        cls, data: dict[str, str], *, session: AsyncSession
    ) -> dict[str, str]:
        data["password"] = get_hashed_password(data["password"])
        user_id = await CRUD.register(data, session)
        verification_token = generate_jwt(user_id, TokenTypes.VERIFICATION, cls._config)
        return {
            "verification_token": verification_token,
            "username": data["username"],
            "email": data["email"],
        }

    @classmethod
    @get_session
    async def verify_email(
        cls, verification_token: str, *, session: AsyncSession
    ) -> None:
        validated, user_id = validate_jwt(
            verification_token, TokenTypes.VERIFICATION, cls._config
        )

        if not validated:
            raise UnauthenticatedError(
                StatusCode.UNAUTHENTICATED, "Verification link is invalid"
            )

        await CRUD.verify_email(user_id, session)
        await cache.delete_many(f"auth-{user_id}", f"profile-{user_id}")

    @classmethod
    @get_session
    async def request_reset_code(
        cls, email: str, *, session: AsyncSession
    ) -> dict[str, str]:
        profile = await CRUD.profile(email, session)
        code = generate_reset_code()
        await cache.set(f"reset-{profile['user_id']}", code, 600)

        result = {
            "user_id": profile["user_id"],
            "username": profile["username"],
            "code": code,
        }
        return result

    @classmethod
    async def validate_reset_code(cls, data: dict[str, str]) -> bool:
        code = await cache.get(f"reset-{data['user_id']}")

        if not code or data["code"] != code:
            return False

        await cache.set(f"reset-{data['user_id']}", "Validated", 600)
        return True

    @classmethod
    @get_session
    async def reset_password(
        cls, data: dict[str, str], *, session: AsyncSession
    ) -> None:
        code = await cache.get(f"reset-{data['user_id']}")

        if not code or code != "Validated":
            raise PermissionError(StatusCode.PERMISSION_DENIED, "Code is not validated")

        data["new_password"] = get_hashed_password(data["new_password"])
        await CRUD.reset_password(data, session)
        await cache.delete(f"reset-{data['user_id']}")

    @classmethod
    @get_session
    async def log_in(
        cls, data: dict[str, str], *, session: AsyncSession
    ) -> dict[str, str | bool]:
        profile = await CRUD.profile(data["username"], session)
        password_is_valid = compare_passwords(data["password"], profile["password"])

        if not password_is_valid:
            raise UnauthenticatedError(
                StatusCode.UNAUTHENTICATED, "Invalid credentials"
            )

        access_token = generate_jwt(profile["user_id"], TokenTypes.ACCESS, cls._config)
        refresh_token = generate_jwt(
            profile["user_id"], TokenTypes.REFRESH, cls._config
        )

        data["user_id"] = profile["user_id"]
        data["access_token"] = access_token
        data["refresh_token"] = refresh_token
        data["browser"] = convert_user_agent(data["user_agent"])
        del data["username"], data["password"], data["user_agent"]
        await CRUD.log_in(data, session)
        await cache.delete(f"session_list-{profile['user_id']}")

        login_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "email": profile["email"],
            "browser": data["browser"],
            "verified": profile["verified"],
        }
        return login_data

    @classmethod
    @get_session
    async def log_out(cls, access_token: str, *, session: AsyncSession) -> None:
        validated, user_id = validate_jwt(access_token, TokenTypes.ACCESS, cls._config)
        db_validated = await CRUD.validate_access_token(access_token, session)

        if not validated or not db_validated:
            raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Token is invalid")

        await CRUD.log_out(access_token, session)
        await cache.delete(f"session_list-{user_id}")

    @classmethod
    @get_session
    async def resend_verification_mail(
        cls, access_token: str, *, session: AsyncSession
    ) -> dict[str, str]:
        validated, user_id = validate_jwt(access_token, TokenTypes.ACCESS, cls._config)
        db_validated = await CRUD.validate_access_token(access_token, session)

        if not validated or not db_validated:
            raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Token is invalid")

        profile = await CRUD.profile(user_id, session)
        verification_token = generate_jwt(user_id, TokenTypes.VERIFICATION, cls._config)

        result = {
            "verification_token": verification_token,
            "username": profile["username"],
            "email": profile["email"],
        }
        return result

    @classmethod
    @get_session
    async def auth(cls, access_token: str, *, session: AsyncSession) -> dict[str, str]:
        validated, user_id = validate_jwt(access_token, TokenTypes.ACCESS, cls._config)
        db_validated = await CRUD.validate_access_token(access_token, session)

        if not validated or not db_validated:
            raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Token is invalid")
        elif cached := await cache.get(f"auth-{user_id}"):
            return cached

        profile = await CRUD.profile(user_id, session)
        user_info = {"user_id": user_id, "verified": profile["verified"]}
        await cache.set(f"auth-{user_id}", user_info, 3600)
        return user_info

    @classmethod
    @get_session
    async def refresh(
        cls, data: dict[str, str], *, session: AsyncSession
    ) -> dict[str, str]:
        validated, user_id = validate_jwt(
            data["refresh_token"], TokenTypes.REFRESH, cls._config
        )
        db_validated = await CRUD.validate_refresh_token(data["refresh_token"], session)

        if not validated or not db_validated:
            raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Token is invalid")

        data["user_id"] = user_id
        data["old_token"] = data["refresh_token"]
        access_token = generate_jwt(user_id, TokenTypes.ACCESS, cls._config)
        refresh_token = generate_jwt(user_id, TokenTypes.REFRESH, cls._config)
        data["access_token"] = access_token
        data["refresh_token"] = refresh_token
        data["browser"] = convert_user_agent(data["user_agent"])
        del data["user_agent"]
        await CRUD.refresh(data, session)
        await cache.delete(f"session_list-{user_id}")

        tokens = {"access_token": access_token, "refresh_token": refresh_token}
        return tokens

    @classmethod
    @get_session
    async def session_list(
        cls, access_token: str, *, session: AsyncSession
    ) -> tuple[dict[str, str]]:
        validated, user_id = validate_jwt(access_token, TokenTypes.ACCESS, cls._config)
        db_validated = await CRUD.validate_access_token(access_token, session)

        if not validated or not db_validated:
            raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Token is invalid")
        elif cached := await cache.get(f"session_list-{user_id}"):
            return cached

        tokens = await CRUD.session_list(user_id, session)

        for token in tokens:
            token["session_id"] = token["token_id"]
            del token["refresh_token"], token["token_id"], token["user_id"]

        await cache.set(f"session_list-{user_id}", tokens, 3600)
        return tokens

    @classmethod
    @get_session
    async def revoke_session(
        cls, data: dict[str, str], *, session: AsyncSession
    ) -> None:
        access_token, refresh_token_id = data["access_token"], data["session_id"]

        access_validated, user_id = validate_jwt(
            access_token, TokenTypes.ACCESS, cls._config
        )
        access_db_validated = await CRUD.validate_access_token(access_token, session)
        refresh_db_validated = await CRUD.validate_refresh_token(
            refresh_token_id, session
        )

        if not access_validated or not access_db_validated or not refresh_db_validated:
            raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Token is invalid")

        await CRUD.revoke_session(refresh_token_id, session)
        await cache.delete(f"session_list-{user_id}")

    @classmethod
    @get_session
    async def profile(
        cls, access_token: str, *, session: AsyncSession
    ) -> dict[str, str]:
        validated, user_id = validate_jwt(access_token, TokenTypes.ACCESS, cls._config)
        db_validated = await CRUD.validate_access_token(access_token, session)

        if not validated or not db_validated:
            raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Token is invalid")
        elif cached := await cache.get(f"profile-{user_id}"):
            return cached

        profile = await CRUD.profile(user_id, session)
        del profile["password"]
        await cache.set(f"profile-{user_id}", profile, 3600)
        return profile

    @classmethod
    @get_session
    async def update_email(
        cls, data: dict[str, str], *, session: AsyncSession
    ) -> dict[str, str]:
        validated, user_id = validate_jwt(
            data["access_token"], TokenTypes.ACCESS, cls._config
        )
        db_validated = await CRUD.validate_access_token(data["access_token"], session)

        if not validated or not db_validated:
            raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Token is invalid")

        data["user_id"] = user_id
        username, email = await CRUD.update_email(data, session)
        await cache.delete(f"profile-{user_id}")

        verification_token = generate_jwt(user_id, TokenTypes.VERIFICATION, cls._config)
        result = {
            "verification_token": verification_token,
            "username": username,
            "email": email,
        }
        return result

    @classmethod
    @get_session
    async def update_password(
        cls, data: dict[str, str], *, session: AsyncSession
    ) -> None:
        validated, user_id = validate_jwt(
            data["access_token"], TokenTypes.ACCESS, cls._config
        )
        db_validated = await CRUD.validate_access_token(data["access_token"], session)

        if not validated or not db_validated:
            raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Token is invalid")

        data["user_id"] = user_id
        data["new_password"] = get_hashed_password(data["new_password"])
        await CRUD.update_password(data, session)

    @classmethod
    @get_session
    async def delete_profile(cls, access_token: str, *, session: AsyncSession) -> str:
        validated, user_id = validate_jwt(access_token, TokenTypes.ACCESS, cls._config)
        db_validated = await CRUD.validate_access_token(access_token, session)

        if not validated or not db_validated:
            raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Token is invalid")

        await CRUD.delete_profile(user_id, session)
        await cache.delete_match(rf"\w+-{user_id}")
        return user_id
