from datetime import datetime as dt
from datetime import timedelta
from enum import Enum
from functools import wraps
from secrets import choice
from typing import Awaitable, Callable, TypeVar

import bcrypt
from grpc import ServicerContext, StatusCode
from httpagentparser import simple_detect
from jwskate import Jwt, SignedJwt
from picologging import Logger
from sqlalchemy.exc import IntegrityError

from config import load_config
from exceptions import UnauthenticatedException

T = TypeVar("T")

config = load_config()


class TokenTypes(Enum):
    ACCESS = 0
    REFRESH = 1
    VERIFICATION = 2


class ExceptionHandler:
    __slots__ = "_logger"

    def __init__(self, logger: Logger):
        self._logger = logger

    async def __call__(
        self,
        context: ServicerContext,
        func: Callable[..., Awaitable[T]],
        *args,
        **kwargs,
    ) -> T:
        try:
            res = await func(*args, **kwargs)
            return res
        except Exception as exc:
            status_code, details = exc.args
            self._logger.error(
                f"Status code: {status_code.name} ({status_code.value[0]}), details: {details}"
            )
            await context.abort(status_code, details)
            raise


def repository_exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            res = await func(*args, **kwargs)
            return res
        except IntegrityError as exc:
            await kwargs["session"].rollback()
            raise exc
        except UnauthenticatedException as exc:
            raise exc
        except Exception as exc:
            await kwargs["session"].rollback()
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    return wrapper


def generate_reset_code() -> str:
    return "".join(choice("0123456789") for _ in range(6))


def generate_jwt(user_id: str, token_type: TokenTypes) -> str:
    match token_type:
        case TokenTypes.ACCESS:
            exp_time = dt.now() + timedelta(minutes=15)
        case TokenTypes.REFRESH:
            exp_time = dt.now() + timedelta(days=30)
        case TokenTypes.VERIFICATION:
            exp_time = dt.now() + timedelta(days=3)
        case _:  # pragma: no cover
            exp_time = None

    claims = {"iss": config.app.name, "sub": user_id, "iat": dt.now(), "exp": exp_time}
    return str(
        Jwt.sign(claims, config.app.private_key, alg="EdDSA", typ=str(token_type.value))
    )


def validate_jwt(token: str, token_type: TokenTypes) -> str:
    jwt = Jwt(token)

    if (
        not isinstance(jwt, SignedJwt)
        or not jwt.verify_signature(config.app.public_key, "EdDSA")
        or jwt.issuer != config.app.name
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
    elif jwt_type == TokenTypes.VERIFICATION and jwt.is_expired():
        raise UnauthenticatedException(
            StatusCode.UNAUTHENTICATED, "Resend the verification mail"
        )
    return jwt.subject


def compare_passwords(password: str, hashed_password: str) -> None:
    if not bcrypt.checkpw(password.encode(), hashed_password.encode()):
        raise UnauthenticatedException(
            StatusCode.UNAUTHENTICATED, "Invalid credentials"
        )


def get_hashed_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def convert_user_agent(user_agent: str) -> str:
    parsed_data = simple_detect(user_agent)
    return f"{parsed_data[1]}, {parsed_data[0]}"
