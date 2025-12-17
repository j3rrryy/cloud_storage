import hashlib
import os
import re
from datetime import datetime, timedelta, timezone
from functools import wraps
from secrets import choice
from typing import Awaitable, Callable, TypeVar

import bcrypt
import inject
import picologging as logging
from grpc import ServicerContext, StatusCode
from httpagentparser import simple_detect
from jwskate import Jwk, Jwt, SignedJwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from enums import TokenTypes
from exceptions import NotFoundException, UnauthenticatedException

T = TypeVar("T")

EMAIL_REGEX = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$")

logger = logging.getLogger()


class KeyPair:
    __slots__ = ("private_key", "public_key")

    def __init__(self):
        self.private_key = Jwk.from_json(os.environ["SECRET_KEY"])
        self.public_key = self.private_key.public_jwk()


class ExceptionHandler:
    @staticmethod
    async def handle(
        context: ServicerContext, func: Callable[..., Awaitable[T]], *args, **kwargs
    ) -> T:
        try:
            return await func(*args, **kwargs)
        except Exception as exc:
            status_code, details = exc.args
            logger.error(
                f"Status code: {status_code.name} ({status_code.value[0]}), details: {details}"
            )
            await context.abort(status_code, details)  # type: ignore
            raise


def with_transaction(func):
    @wraps(func)
    @inject.autoparams()
    async def wrapper(*args, session: AsyncSession, **kwargs):
        try:
            return await func(*args, session, **kwargs)
        except Exception as exc:
            await session.rollback()
            if not isinstance(
                exc, (IntegrityError, NotFoundException, UnauthenticatedException)
            ):
                exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    return wrapper


def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def generate_reset_code() -> str:
    return "".join(choice("0123456789") for _ in range(6))


@inject.autoparams()
def generate_jwt(user_id: str, token_type: TokenTypes, key_pair: KeyPair) -> str:
    match token_type:
        case TokenTypes.ACCESS:
            exp_time = datetime.now() + timedelta(minutes=15)
        case TokenTypes.REFRESH:
            exp_time = datetime.now() + timedelta(days=30)
        case TokenTypes.EMAIL_CONFIRMATION:
            exp_time = datetime.now() + timedelta(days=3)
        case _:  # pragma: no cover
            exp_time = None

    claims = {
        "iss": os.environ["APP_NAME"],
        "sub": user_id,
        "iat": datetime.now(),
        "exp": exp_time,
    }
    return str(
        Jwt.sign(claims, key_pair.private_key, alg="EdDSA", typ=str(token_type.value))
    )


@inject.autoparams()
def validate_jwt(token: str, token_type: TokenTypes, key_pair: KeyPair) -> Jwt:
    jwt = Jwt(token)

    if (
        not isinstance(jwt, SignedJwt)
        or not jwt.verify_signature(key_pair.public_key, "EdDSA")
        or jwt.issuer != os.environ["APP_NAME"]
        or jwt.subject is None
        or not (
            hasattr(jwt, "typ") and jwt.typ.isdigit() and int(jwt.typ) in range(0, 3)
        )
    ):
        raise UnauthenticatedException(StatusCode.UNAUTHENTICATED, "Token is invalid")

    jwt_type = TokenTypes(int(jwt.typ))

    if jwt_type != token_type:
        raise UnauthenticatedException(StatusCode.UNAUTHENTICATED, "Invalid token type")
    elif jwt_type == TokenTypes.ACCESS and jwt.is_expired():
        raise UnauthenticatedException(StatusCode.UNAUTHENTICATED, "Refresh the tokens")
    elif jwt_type == TokenTypes.REFRESH and jwt.is_expired():
        raise UnauthenticatedException(StatusCode.UNAUTHENTICATED, "Re-log in")
    elif jwt_type == TokenTypes.EMAIL_CONFIRMATION and jwt.is_expired():
        raise UnauthenticatedException(
            StatusCode.UNAUTHENTICATED, "Resend the email confirmation mail"
        )
    return jwt


def validate_jwt_and_get_user_id(token: str, token_type: TokenTypes) -> str:
    return validate_jwt(token, token_type).subject  # type: ignore


def get_hashed_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def compare_passwords(password: str, hashed_password: str) -> None:
    if not bcrypt.checkpw(password.encode(), hashed_password.encode()):
        raise UnauthenticatedException(
            StatusCode.UNAUTHENTICATED, "Invalid credentials"
        )


def get_hashed_jwt(jwt: str) -> str:
    return hashlib.sha256(jwt.encode()).hexdigest()


def convert_user_agent(user_agent: str) -> str:
    parsed_data = simple_detect(user_agent)
    return f"{parsed_data[1]}, {parsed_data[0]}"


def user_profile_key(user_id: str) -> str:
    return f"user:{user_id}:profile"


def user_session_list_key(user_id: str) -> str:
    return f"user:{user_id}:session_list"


def user_reset_key(user_id: str) -> str:
    return f"user:{user_id}:reset"


def access_token_key(access_token: str) -> str:
    return f"token:access:{access_token}"


def user_all_keys(user_id: str) -> list[str]:
    return [
        user_profile_key(user_id),
        user_session_list_key(user_id),
        user_reset_key(user_id),
    ]
