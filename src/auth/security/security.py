import base64
from datetime import timedelta
from secrets import randbelow

from blake3 import blake3
from jwskate import Jwk, Jwt, SignedJwt

from config import setup_password_hasher
from enums import TokenType
from exceptions import UnauthenticatedException
from settings import Settings
from utils import utc_now_aware

PRIVATE_KEY = Jwk.from_pem(base64.b64decode(Settings.SECRET_KEY))
PUBLIC_KEY = PRIVATE_KEY.public_jwk()

PASSWORD_HASHER = setup_password_hasher()


def generate_jwt(user_id: str, token_type: TokenType) -> str:
    now = utc_now_aware()
    match token_type:
        case TokenType.ACCESS:
            exp_time = now + timedelta(minutes=15)
        case TokenType.REFRESH:
            exp_time = now + timedelta(days=30)
        case TokenType.EMAIL_CONFIRMATION:
            exp_time = now + timedelta(days=3)
        case _:  # pragma: no cover
            exp_time = None

    claims = {
        "iss": Settings.APP_NAME,
        "sub": user_id,
        "iat": now,
        "exp": exp_time,
    }
    return str(Jwt.sign(claims, PRIVATE_KEY, alg="EdDSA", typ=str(token_type.value)))


def validate_jwt(token: str, token_type: TokenType) -> SignedJwt:
    jwt = Jwt(token)

    if (
        not isinstance(jwt, SignedJwt)
        or not jwt.verify_signature(PUBLIC_KEY, "EdDSA")
        or jwt.issuer != Settings.APP_NAME
        or jwt.subject is None
        or not (hasattr(jwt, "typ") and jwt.typ.isdigit() and int(jwt.typ) in {0, 1, 2})
    ):
        raise UnauthenticatedException("Token is invalid")

    jwt_type = TokenType(int(jwt.typ))

    if jwt_type != token_type:
        raise UnauthenticatedException("Invalid token type")
    if jwt.is_expired():
        match jwt_type:
            case TokenType.ACCESS:
                raise UnauthenticatedException("Refresh the tokens")
            case TokenType.REFRESH:
                raise UnauthenticatedException("Re-log in")
            case TokenType.EMAIL_CONFIRMATION:
                raise UnauthenticatedException("Resend the email confirmation mail")
            case _:  # pragma: no cover
                pass
    return jwt


def validate_jwt_and_get_user_id(token: str, token_type: TokenType) -> str:
    return validate_jwt(token, token_type).subject  # type: ignore


def get_jwt_hash(jwt: str) -> str:
    return blake3(jwt.encode()).hexdigest()


def get_password_hash(password: str) -> str:
    return PASSWORD_HASHER.hash(password)


def compare_passwords(hashed_password: str, password: str) -> None:
    try:
        PASSWORD_HASHER.verify(hashed_password, password)
    except Exception:
        raise UnauthenticatedException("Invalid credentials")


def generate_code(length: int = 6) -> str:
    return "".join(str(randbelow(10)) for _ in range(length))
