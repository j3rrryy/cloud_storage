import base64
import hashlib
from datetime import datetime, timedelta
from secrets import choice

import bcrypt
from jwskate import Jwk, Jwt, SignedJwt

from enums import TokenTypes
from exceptions import UnauthenticatedException
from settings import Settings


class KeyPair:
    PRIVATE_KEY = Jwk.from_pem(base64.b64decode(Settings.SECRET_KEY))
    PUBLIC_KEY = PRIVATE_KEY.public_jwk()


def generate_jwt(user_id: str, token_type: TokenTypes) -> str:
    match token_type:
        case TokenTypes.ACCESS:
            exp_time = datetime.now() + timedelta(minutes=15)
        case TokenTypes.REFRESH:
            exp_time = datetime.now() + timedelta(days=30)
        case TokenTypes.EMAIL_CONFIRMATION:
            exp_time = datetime.now() + timedelta(days=3)

    claims = {
        "iss": Settings.APP_NAME,
        "sub": user_id,
        "iat": datetime.now(),
        "exp": exp_time,
    }
    return str(
        Jwt.sign(claims, KeyPair.PRIVATE_KEY, alg="EdDSA", typ=str(token_type.value))
    )


def validate_jwt(token: str, token_type: TokenTypes) -> SignedJwt:
    jwt = Jwt(token)

    if (
        not isinstance(jwt, SignedJwt)
        or not jwt.verify_signature(KeyPair.PUBLIC_KEY, "EdDSA")
        or jwt.issuer != Settings.APP_NAME
        or jwt.subject is None
        or not (
            hasattr(jwt, "typ") and jwt.typ.isdigit() and int(jwt.typ) in range(0, 3)
        )
    ):
        raise UnauthenticatedException("Token is invalid")

    jwt_type = TokenTypes(int(jwt.typ))

    if jwt_type != token_type:
        raise UnauthenticatedException("Invalid token type")
    if jwt.is_expired():
        match jwt_type:
            case TokenTypes.ACCESS:
                raise UnauthenticatedException("Refresh the tokens")
            case TokenTypes.REFRESH:
                raise UnauthenticatedException("Re-log in")
            case TokenTypes.EMAIL_CONFIRMATION:
                raise UnauthenticatedException("Resend the email confirmation mail")
    return jwt


def validate_jwt_and_get_user_id(token: str, token_type: TokenTypes) -> str:
    return validate_jwt(token, token_type).subject  # type: ignore


def get_jwt_hash(jwt: str) -> str:
    return hashlib.sha256(jwt.encode()).hexdigest()


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def compare_passwords(password: str, hashed_password: str) -> None:
    if not bcrypt.checkpw(password.encode(), hashed_password.encode()):
        raise UnauthenticatedException("Invalid credentials")


def generate_code(length: int = 6) -> str:
    return "".join(choice("0123456789") for _ in range(length))
