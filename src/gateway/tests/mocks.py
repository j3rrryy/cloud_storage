import datetime
from unittest.mock import AsyncMock, MagicMock

from google.protobuf.empty_pb2 import Empty
from google.protobuf.timestamp_pb2 import Timestamp

from proto import auth_pb2, file_pb2

TIMESTAMP = datetime.datetime(1970, 1, 1, 0, 2, 3)
TIMESTAMP_MOCK = Timestamp(seconds=123)

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
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
)
BROWSER = "Firefox 47.0, Windows 7"


UPLOAD_ID = "YjUzZjE5MzktY2U2Zi00NmNiLWE3Y2ItNmUwY2M2ODE3NDA5LjBmNzcyN2I0LTNkZjgtNGQ0ZS1hNTc3LTRiMmRjOTFjOTc2ZXgxNzYyOTAwNTgxNzg3NDgwOTI5"
URL = "/s3-files/662c3e99-65dc-4a26-a2c2-bbd9f4e1fac4?AWSAccessKeyId=test_username&Signature=kn3PpoJ%2BwQBYVmpYl%2B8cZK2KM0s%3D&Expires=1741791573"
ETAG = "fac024381d213f9949facd263b44aea4"
FILE_ID = "b8a47c8d-9203-456a-aa58-ceab64b13cbb"
SIZE = 123
NAME = "test_name"


def create_auth_stub_v1() -> MagicMock:
    stub = MagicMock()

    stub.Register = AsyncMock(
        return_value=auth_pb2.VerificationMail(
            verification_token=VERIFICATION_TOKEN, username=USERNAME, email=EMAIL
        )
    )
    stub.VerifyEmail = AsyncMock(return_value=Empty())
    stub.RequestResetCode = AsyncMock(
        return_value=auth_pb2.ResetCodeResponse(
            user_id=USER_ID, username=USERNAME, code=CODE
        )
    )
    stub.ValidateResetCode = AsyncMock(return_value=auth_pb2.CodeIsValid(is_valid=True))
    stub.ResetPassword = AsyncMock(return_value=Empty())
    stub.LogIn = AsyncMock(
        return_value=auth_pb2.LogInResponse(
            access_token=ACCESS_TOKEN,
            refresh_token=REFRESH_TOKEN,
            email=EMAIL,
            browser=BROWSER,
            verified=True,
        )
    )
    stub.LogOut = AsyncMock(return_value=Empty())
    stub.ResendVerificationMail = AsyncMock(
        return_value=auth_pb2.VerificationMail(
            verification_token=VERIFICATION_TOKEN, username=USERNAME, email=EMAIL
        )
    )
    stub.Auth = AsyncMock(return_value=auth_pb2.UserId(user_id=USER_ID))
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
                    created_at=TIMESTAMP_MOCK,
                ),
            )
        )
    )
    stub.RevokeSession = AsyncMock(return_value=Empty())
    stub.Profile = AsyncMock(
        return_value=auth_pb2.ProfileResponse(
            user_id=USER_ID,
            username=USERNAME,
            email=EMAIL,
            verified=True,
            registered_at=TIMESTAMP_MOCK,
        )
    )
    stub.UpdateEmail = AsyncMock(
        return_value=auth_pb2.VerificationMail(
            verification_token=VERIFICATION_TOKEN, username=USERNAME, email=EMAIL
        )
    )
    stub.UpdatePassword = AsyncMock(return_value=Empty())
    stub.DeleteProfile = AsyncMock(return_value=auth_pb2.UserId(user_id=USER_ID))
    return stub


def create_file_stub_v1() -> MagicMock:
    stub = MagicMock()

    stub.InitiateUpload = AsyncMock(
        return_value=file_pb2.InitiateUploadResponse(
            upload_id=UPLOAD_ID,
            part_size=SIZE,
            parts=[file_pb2.UploadPart(part_number=1, url=URL)],
        )
    )
    stub.CompleteUpload = AsyncMock(return_value=Empty())
    stub.AbortUpload = AsyncMock(return_value=Empty())
    stub.FileInfo = AsyncMock(
        return_value=file_pb2.FileInfoResponse(
            file_id=FILE_ID, name=NAME, size=SIZE, uploaded_at=TIMESTAMP_MOCK
        )
    )
    stub.FileList = AsyncMock(
        return_value=file_pb2.FileListResponse(
            files=(
                file_pb2.FileInfoResponse(
                    file_id=FILE_ID,
                    name=NAME,
                    size=SIZE,
                    uploaded_at=TIMESTAMP_MOCK,
                ),
            )
        )
    )
    stub.Download = AsyncMock(return_value=file_pb2.URL(url=URL))
    stub.Delete = AsyncMock(return_value=Empty())
    stub.DeleteAll = AsyncMock(return_value=Empty())
    return stub


def create_mail_producer() -> AsyncMock:
    producer = AsyncMock()
    return producer
