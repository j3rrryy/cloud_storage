from datetime import datetime as dt
from datetime import timedelta
from enum import Enum
from secrets import choice
from typing import Any

import bcrypt
from grpc import ServicerContext, StatusCode
from httpagentparser import simple_detect
from jwskate import Jwt
from picologging import Logger

from config import Config
from errors import UnauthenticatedError


class TokenTypes(Enum):
    ACCESS = 0
    REFRESH = 1
    VERIFICATION = 2


class ExceptionHandler:
    __slots__ = "_logger"

    def __init__(self, logger: Logger):
        self._logger = logger

    async def __call__(self, context: ServicerContext, func, *args, **kwargs) -> Any:
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as exc:
            status_code, details = exc.args
            self._logger.error(
                f"Status code: {status_code.name} ({status_code.value[0]}), details: {details}"
            )
            await context.abort(status_code, details)


def generate_reset_code() -> str:
    return "".join(choice("0123456789") for _ in range(6))


def generate_jwt(user_id: str, token_type: TokenTypes, config: Config) -> str:
    match token_type:
        case TokenTypes.ACCESS:
            exp_time = dt.now() + timedelta(minutes=15)
        case TokenTypes.REFRESH:
            exp_time = dt.now() + timedelta(days=30)
        case TokenTypes.VERIFICATION:
            exp_time = dt.now() + timedelta(days=3)

    claims = {
        "type": token_type.value,
        "iss": config.app.name,
        "sub": user_id,
        "iat": dt.now(),
        "exp": exp_time,
    }
    jwt = str(Jwt.sign(claims, key=config.app.private_key, alg="EdDSA"))
    return jwt


def validate_jwt(
    token: str, token_type: TokenTypes, config: Config
) -> tuple[bool, str | None]:
    try:
        jwt = Jwt(token)
        jwt_type = TokenTypes(jwt.type)

        verified_signature = jwt.verify_signature(config.app.public_key, alg="EdDSA")
        verified_token_type = jwt_type == token_type
        verified_issuer = jwt.issuer == config.app.name
        user_id = jwt.subject
        expired = jwt.is_expired()

        if not verified_token_type:
            raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Invalid token type")
        elif jwt_type == TokenTypes.ACCESS and expired:
            raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Refresh the tokens")
        elif jwt_type == TokenTypes.REFRESH and expired:
            raise UnauthenticatedError(
                StatusCode.UNAUTHENTICATED, "Resend the verification mail"
            )

        result = (
            verified_signature
            and verified_token_type
            and verified_issuer
            and user_id
            and not expired
        )

        return result, user_id
    except UnauthenticatedError as exc:
        raise exc
    except Exception:
        raise UnauthenticatedError(StatusCode.UNAUTHENTICATED, "Token is invalid")


def compare_passwords(password: str, hashed_password: str) -> bool:
    result = bcrypt.checkpw(password.encode(), hashed_password.encode())
    return result


def get_hashed_password(password: str) -> str:
    result = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return result


def convert_user_agent(user_agent: str) -> str:
    parsed_data = simple_detect(user_agent)
    return f"{parsed_data[1]}, {parsed_data[0]}"
