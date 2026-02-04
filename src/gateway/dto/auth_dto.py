import datetime
from dataclasses import dataclass

from .base_dto import FromResponseMixin, FromSchemaMixin, ToRequestMixin, ToSchemaMixin


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
    browser: str
    email_confirmed: bool


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
    browser: str
    created_at: datetime.datetime


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
