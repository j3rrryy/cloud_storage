from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from dto import response as response_dto
from utils import get_hashed_password

ACCESS_TOKEN = "eyJ0eXBlIjowLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.fyxQuUSic9USlnl9vXYYIelRBTaxsdILiosQHVIOUlU"
REFRESH_TOKEN = "eyJ0eXBlIjoxLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.Cz6F9m9TJP76hzcyst0xE9vp6RmXtGIhAXaNqJWrJL8"
VERIFICATION_TOKEN = "eyJ0eXBlIjoyLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.1ukhU0OncZBofD_z3O5q5wrhoHaRm_RtAZAtqxI6CUY"
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


def create_repository() -> MagicMock:
    crud = MagicMock()

    crud.register = AsyncMock(return_value=USER_ID)
    crud.verify_email = AsyncMock()
    crud.reset_password = AsyncMock()
    crud.log_in = AsyncMock()
    crud.log_out = AsyncMock()
    crud.refresh = AsyncMock()
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
            ),
        )
    )
    crud.revoke_session = AsyncMock()
    crud.validate_access_token = AsyncMock()
    crud.profile = AsyncMock(
        return_value=response_dto.ProfileResponseDTO(
            USER_ID, USERNAME, EMAIL, get_hashed_password(PASSWORD), True, TIMESTAMP
        )
    )
    crud.update_email = AsyncMock(return_value=USERNAME)
    crud.update_password = AsyncMock()
    crud.delete_profile = AsyncMock()
    return crud


def create_cache() -> MagicMock:
    cache = MagicMock()

    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()
    cache.delete = AsyncMock()
    cache.delete_many = AsyncMock()
    cache.delete_match = AsyncMock()
    return cache
