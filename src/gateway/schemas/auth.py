import datetime
from typing import Annotated
from uuid import UUID

from msgspec import Meta

from .base import BaseStruct


class Registration(BaseStruct):
    username: Annotated[str, Meta(pattern=r"^\w{3,20}$")]
    email: Annotated[
        str,
        Meta(
            pattern=r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$",
            examples=["example@gmail.com"],
        ),
    ]
    password: Annotated[str, Meta(min_length=8, max_length=30)]


class ForgotPassword(BaseStruct):
    email: Annotated[
        str,
        Meta(
            pattern=r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$",
            examples=["example@gmail.com"],
        ),
    ]


class ResetCode(BaseStruct):
    user_id: UUID
    code: Annotated[
        str,
        Meta(
            min_length=6,
            max_length=6,
            examples=["123456"],
        ),
    ]


class CodeIsValid(BaseStruct):
    is_valid: bool = False


class ResetPassword(BaseStruct):
    user_id: UUID
    new_password: Annotated[str, Meta(min_length=8, max_length=30)]


class LogIn(BaseStruct):
    username: Annotated[str, Meta(pattern=r"^\w{3,20}$")]
    password: Annotated[str, Meta(min_length=8, max_length=30)]


class Tokens(BaseStruct):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class Auth(BaseStruct):
    user_id: UUID
    verified: bool = False


class UserId(BaseStruct):
    user_id: UUID


class RefreshToken(BaseStruct):
    refresh_token: str


class SessionId(BaseStruct):
    session_id: UUID


class SessionInfo(BaseStruct):
    session_id: UUID
    user_ip: str
    browser: str
    last_accessed: datetime.datetime


class SessionList(BaseStruct):
    sessions: tuple[SessionInfo]


class Profile(BaseStruct):
    user_id: UUID
    username: str
    email: Annotated[
        str,
        Meta(
            pattern=r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$",
            examples=["example@gmail.com"],
        ),
    ]
    registered: datetime.datetime
    verified: bool = False


class UpdateEmail(BaseStruct):
    new_email: Annotated[
        str,
        Meta(
            pattern=r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$",
            examples=["example@gmail.com"],
        ),
    ]


class UpdatePassword(BaseStruct):
    old_password: Annotated[str, Meta(min_length=8, max_length=30)]
    new_password: Annotated[str, Meta(min_length=8, max_length=30)]
