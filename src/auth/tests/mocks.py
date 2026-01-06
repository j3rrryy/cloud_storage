from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from cashews import Cache
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from dto import response as response_dto
from repository import AuthRepository, TokenPair, User
from security import get_password_hash

ACCESS_TOKEN = "eyJ0eXBlIjowLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.fyxQuUSic9USlnl9vXYYIelRBTaxsdILiosQHVIOUlU"
REFRESH_TOKEN = "eyJ0eXBlIjoxLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.Cz6F9m9TJP76hzcyst0xE9vp6RmXtGIhAXaNqJWrJL8"
CONFIRMATION_TOKEN = "eyJ0eXBlIjoyLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.1ukhU0OncZBofD_z3O5q5wrhoHaRm_RtAZAtqxI6CUY"
CODE = "123456"

USER_ID = "00e51a90-0f94-4ecb-8dd1-399ba409508e"
USERNAME = "test_username"
EMAIL = "test@example.com"
PASSWORD = "p@ssw0rd"
TIMESTAMP = datetime.fromisoformat("1970-01-01T00:02:03Z")

SESSION_ID = "13bcdea3-dd61-40fb-8f1f-f9546fd8ffc5"
USER_IP = "127.0.0.1"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
)
BROWSER = "Firefox 47.0, Windows 7"


def create_session() -> AsyncSession:
    return AsyncMock(spec=AsyncSession)


def create_sessionmaker(session) -> async_sessionmaker[AsyncSession]:
    sessionmaker = MagicMock(spec=async_sessionmaker[AsyncSession])
    sessionmaker.return_value.__aenter__.return_value = session
    sessionmaker.begin.return_value.__aenter__.return_value = session
    return sessionmaker


def create_cache() -> Cache:
    return AsyncMock(spec=Cache)


def create_auth_repository() -> AuthRepository:
    crud = AsyncMock(spec=AuthRepository)
    crud.register = AsyncMock(return_value=USER_ID)
    crud.session_list = AsyncMock(
        return_value=(
            response_dto.SessionInfoResponseDTO(
                SESSION_ID,
                USER_ID,
                ACCESS_TOKEN,
                REFRESH_TOKEN,
                USER_IP,
                BROWSER,
                TIMESTAMP,
            )
        )
    )
    crud.profile_by_user_id = AsyncMock(
        return_value=response_dto.ProfileResponseDTO(
            USER_ID, USERNAME, EMAIL, get_password_hash(PASSWORD), False, TIMESTAMP
        )
    )
    crud.profile_by_username = AsyncMock(
        return_value=response_dto.ProfileResponseDTO(
            USER_ID, USERNAME, EMAIL, get_password_hash(PASSWORD), False, TIMESTAMP
        )
    )
    crud.profile_by_email = AsyncMock(
        return_value=response_dto.ProfileResponseDTO(
            USER_ID, USERNAME, EMAIL, get_password_hash(PASSWORD), False, TIMESTAMP
        )
    )
    crud.update_email = AsyncMock(return_value=USERNAME)
    return crud


def create_user() -> User:
    return User(
        user_id=USER_ID,
        username=USERNAME,
        email=EMAIL,
        password=get_password_hash(PASSWORD),
        email_confirmed=False,
        registered_at=TIMESTAMP,
    )


def create_token_pair() -> TokenPair:
    return TokenPair(
        session_id=SESSION_ID,
        user_id=USER_ID,
        access_token=ACCESS_TOKEN,
        refresh_token=REFRESH_TOKEN,
        user_ip=USER_IP,
        browser=BROWSER,
        created_at=TIMESTAMP,
    )
