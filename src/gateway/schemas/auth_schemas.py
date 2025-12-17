import datetime
from typing import Annotated

from msgspec import Meta, Struct

EMAIL_REGEX = r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$"
EMAIL_EXAMPLES = ["example@gmail.com"]

UUID4_REGEX = r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$"
UUID4_EXAMPLES = ["123e4567-e89b-12d3-a456-426614174000"]


class Registration(Struct):
    username: Annotated[str, Meta(pattern=r"^\w{3,20}$")]
    email: Annotated[
        str, Meta(pattern=EMAIL_REGEX, max_length=255, examples=EMAIL_EXAMPLES)
    ]
    password: Annotated[str, Meta(min_length=8, max_length=30)]


class ForgotPassword(Struct):
    email: Annotated[
        str, Meta(pattern=EMAIL_REGEX, max_length=255, examples=EMAIL_EXAMPLES)
    ]


class ResetCode(Struct):
    user_id: Annotated[str, Meta(pattern=UUID4_REGEX, examples=UUID4_EXAMPLES)]
    code: Annotated[str, Meta(min_length=6, max_length=6, examples=["123456"])]


class CodeIsValid(Struct):
    is_valid: bool


class ResetPassword(Struct):
    user_id: Annotated[str, Meta(pattern=UUID4_REGEX, examples=UUID4_EXAMPLES)]
    new_password: Annotated[str, Meta(min_length=8, max_length=30)]


class LogIn(Struct):
    username: Annotated[str, Meta(pattern=r"^\w{3,20}$")]
    password: Annotated[str, Meta(min_length=8, max_length=30)]


class Tokens(Struct):
    access_token: Annotated[str, Meta(max_length=350)]
    refresh_token: Annotated[str, Meta(max_length=350)]


class UserId(Struct):
    user_id: Annotated[str, Meta(pattern=UUID4_REGEX, examples=UUID4_EXAMPLES)]


class RefreshToken(Struct):
    refresh_token: Annotated[str, Meta(max_length=350)]


class SessionId(Struct):
    session_id: Annotated[str, Meta(pattern=UUID4_REGEX, examples=UUID4_EXAMPLES)]


class SessionInfo(Struct):
    session_id: Annotated[str, Meta(pattern=UUID4_REGEX, examples=UUID4_EXAMPLES)]
    user_ip: Annotated[str, Meta(min_length=7, max_length=15)]
    browser: Annotated[str, Meta(max_length=150)]
    created_at: datetime.datetime


class SessionList(Struct):
    sessions: list[SessionInfo]


class Profile(Struct):
    user_id: Annotated[str, Meta(pattern=UUID4_REGEX, examples=UUID4_EXAMPLES)]
    username: Annotated[str, Meta(pattern=r"^\w{3,20}$")]
    email: Annotated[
        str, Meta(pattern=EMAIL_REGEX, max_length=255, examples=EMAIL_EXAMPLES)
    ]
    email_confirmed: bool
    registered_at: datetime.datetime


class UpdateEmail(Struct):
    new_email: Annotated[str, Meta(pattern=EMAIL_REGEX, examples=EMAIL_EXAMPLES)]


class UpdatePassword(Struct):
    old_password: Annotated[str, Meta(min_length=8, max_length=30)]
    new_password: Annotated[str, Meta(min_length=8, max_length=30)]
