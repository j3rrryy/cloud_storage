from unittest.mock import AsyncMock, MagicMock

from google.protobuf import empty_pb2, timestamp_pb2

from proto import auth_pb2, files_pb2

TIMESTAMP = "1970-01-01T00:02:03Z"
TIMESTAMP_MOCK = timestamp_pb2.Timestamp(seconds=123)


ACCESS_TOKEN = "eyJ0eXBlIjowLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.fyxQuUSic9USlnl9vXYYIelRBTaxsdILiosQHVIOUlU"
REFRESH_TOKEN = "eyJ0eXBlIjoxLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.Cz6F9m9TJP76hzcyst0xE9vp6RmXtGIhAXaNqJWrJL8"
VERIFICATION_TOKEN = "eyJ0eXBlIjoyLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.1ukhU0OncZBofD_z3O5q5wrhoHaRm_RtAZAtqxI6CUY"
CODE = "123456"

USER_ID = "00e51a90-0f94-4ecb-8dd1-399ba409508e"
USERNAME = "test_username"
EMAIL = "test@example.com"
PASSWORD = "p@ssw0rd"

SESSION_ID = "13bcdea3-dd61-40fb-8f1f-f9546fd8ffc5"
USER_IP = "127.0.0.1"
USER_AGENT = "test_user_agent"
BROWSER = "test_browser"


URL = "/files/url"
FILE_ID = "b8a47c8d-9203-456a-aa58-ceab64b13cbb"
PATH = "/"
SIZE = 123
NAME = "test_name"


def create_auth_stub(verified: bool) -> MagicMock:
    stub = MagicMock()

    stub.Register = AsyncMock(
        return_value=auth_pb2.VerificationMail(
            verification_token=VERIFICATION_TOKEN, username=USERNAME, email=EMAIL
        )
    )
    stub.VerifyEmail = AsyncMock(return_value=empty_pb2.Empty())
    stub.RequestResetCode = AsyncMock(
        return_value=auth_pb2.ResetCodeResponse(
            user_id=USER_ID, username=USERNAME, code=CODE
        )
    )
    stub.ValidateResetCode = AsyncMock(return_value=auth_pb2.CodeIsValid(is_valid=True))
    stub.ResetPassword = AsyncMock(return_value=empty_pb2.Empty())
    stub.LogIn = AsyncMock(
        return_value=auth_pb2.LogInResponse(
            access_token=ACCESS_TOKEN,
            refresh_token=REFRESH_TOKEN,
            email=EMAIL,
            browser=BROWSER,
            verified=verified,
        )
    )
    stub.LogOut = AsyncMock(return_value=empty_pb2.Empty())
    stub.ResendVerificationMail = AsyncMock(
        return_value=auth_pb2.VerificationMail(
            verification_token=VERIFICATION_TOKEN, username=USERNAME, email=EMAIL
        )
    )
    stub.Auth = AsyncMock(
        return_value=auth_pb2.AuthResponse(user_id=USER_ID, verified=verified)
    )
    stub.Refresh = AsyncMock(
        return_value=auth_pb2.Tokens(
            access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN
        )
    )
    stub.SessionList = AsyncMock(
        return_value=auth_pb2.Sessions(
            sessions=(
                auth_pb2.SessionInfo(
                    session_id=SESSION_ID,
                    user_ip=USER_IP,
                    browser=BROWSER,
                    last_accessed=TIMESTAMP_MOCK,
                ),
            )
        )
    )
    stub.RevokeSession = AsyncMock(return_value=empty_pb2.Empty())
    stub.Profile = AsyncMock(
        return_value=auth_pb2.ProfileResponse(
            user_id=USER_ID,
            username=USERNAME,
            email=EMAIL,
            verified=verified,
            registered=TIMESTAMP_MOCK,
        )
    )
    stub.UpdateEmail = AsyncMock(
        return_value=auth_pb2.VerificationMail(
            verification_token=VERIFICATION_TOKEN, username=USERNAME, email=EMAIL
        )
    )
    stub.UpdatePassword = AsyncMock(return_value=empty_pb2.Empty())
    stub.DeleteProfile = AsyncMock(return_value=auth_pb2.UserId(user_id=USER_ID))
    return stub


def create_files_stub() -> MagicMock:
    stub = MagicMock()

    stub.UploadFile = AsyncMock(return_value=files_pb2.FileURLResponse(url=URL))
    stub.FileInfo = AsyncMock(
        return_value=files_pb2.FileInfoResponse(
            file_id=FILE_ID, name=NAME, path=PATH, size=SIZE, uploaded=TIMESTAMP_MOCK
        )
    )
    stub.FileList = AsyncMock(
        return_value=files_pb2.FileListResponse(
            files=(
                files_pb2.FileInfoResponse(
                    file_id=FILE_ID,
                    name=NAME,
                    path=PATH,
                    size=SIZE,
                    uploaded=TIMESTAMP_MOCK,
                ),
            )
        )
    )
    stub.DownloadFile = AsyncMock(return_value=files_pb2.FileURLResponse(url=URL))
    stub.DeleteFiles = AsyncMock(return_value=empty_pb2.Empty())
    stub.DeleteAllFiles = AsyncMock(return_value=empty_pb2.Empty())
    return stub


def create_mail_producer() -> AsyncMock:
    producer = AsyncMock()
    return producer
