import datetime
from dataclasses import dataclass
from typing import Type, cast

from proto import auth_pb2 as pb2

from .base_dto import (
    FromResponseMixin,
    FromSchemaMixin,
    Message,
    ToRequestMixin,
    ToSchemaMixin,
)


@dataclass(slots=True, frozen=True)
class RegistrationDTO(FromSchemaMixin, ToRequestMixin):
    username: str
    email: str
    password: str


@dataclass(slots=True, frozen=True)
class ResetInfoDTO(FromResponseMixin):
    user_id: str
    username: str
    code: str


@dataclass(slots=True, frozen=True)
class ResetCodeDTO(FromSchemaMixin, ToRequestMixin):
    user_id: str
    code: str


@dataclass(slots=True, frozen=True)
class ResetPasswordDTO(FromSchemaMixin, ToRequestMixin):
    user_id: str
    new_password: str


@dataclass(slots=True, frozen=True)
class LogInDTO(ToRequestMixin):
    username: str
    password: str
    user_ip: str
    user_agent: str


@dataclass(slots=True, frozen=True)
class LogInDataDTO(FromResponseMixin, ToSchemaMixin):
    access_token: str
    refresh_token: str
    email: str
    country_code: str | None
    browser: str
    email_confirmed: bool

    @classmethod
    def from_response(cls: Type["LogInDataDTO"], message: Message) -> "LogInDataDTO":
        message = cast(pb2.LogInResponse, message)
        country_code = message.country_code
        return LogInDataDTO(
            message.access_token,
            message.refresh_token,
            message.email,
            country_code if country_code else None,
            message.browser,
            message.email_confirmed,
        )


@dataclass(slots=True, frozen=True)
class RefreshDTO(ToRequestMixin):
    refresh_token: str
    user_ip: str
    user_agent: str


@dataclass(slots=True, frozen=True)
class TokensDTO(FromResponseMixin, ToSchemaMixin):
    access_token: str
    refresh_token: str


@dataclass(slots=True, frozen=True)
class SessionDTO(FromResponseMixin, ToSchemaMixin):
    session_id: str
    user_ip: str
    country_code: str | None
    browser: str
    created_at: datetime.datetime

    @classmethod
    def from_response(cls: Type["SessionDTO"], message: Message) -> "SessionDTO":
        message = cast(pb2.SessionInfo, message)
        country_code = message.country_code
        return SessionDTO(
            message.session_id,
            message.user_ip,
            country_code if country_code else None,
            message.browser,
            message.created_at.ToDatetime(),
        )


@dataclass(slots=True, frozen=True)
class RevokeSessionDTO(ToRequestMixin):
    access_token: str
    session_id: str


@dataclass(slots=True, frozen=True)
class ProfileDTO(FromResponseMixin, ToSchemaMixin):
    user_id: str
    username: str
    email: str
    registered_at: datetime.datetime
    email_confirmed: bool


@dataclass(slots=True, frozen=True)
class UpdateEmailDTO(ToRequestMixin):
    access_token: str
    new_email: str


@dataclass(slots=True, frozen=True)
class UpdatePasswordDTO(ToRequestMixin):
    access_token: str
    old_password: str
    new_password: str
