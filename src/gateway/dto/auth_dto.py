import datetime
from dataclasses import dataclass

from .base_dto import BaseDTO


@dataclass(slots=True, frozen=True)
class RegistrationDTO(BaseDTO):
    username: str
    email: str
    password: str


@dataclass(slots=True, frozen=True)
class ResetInfoDTO(BaseDTO):
    user_id: str
    username: str
    code: str


@dataclass(slots=True, frozen=True)
class ResetCodeDTO(BaseDTO):
    user_id: str
    code: str


@dataclass(slots=True, frozen=True)
class ResetPasswordDTO(BaseDTO):
    user_id: str
    new_password: str


@dataclass(slots=True, frozen=True)
class LogInDTO(BaseDTO):
    username: str
    password: str
    user_ip: str
    user_agent: str


@dataclass(slots=True, frozen=True)
class LogInDataDTO(BaseDTO):
    access_token: str
    refresh_token: str
    email: str
    browser: str
    verified: bool = False


@dataclass(slots=True, frozen=True)
class RefreshDTO(BaseDTO):
    refresh_token: str
    user_ip: str
    user_agent: str


@dataclass(slots=True, frozen=True)
class TokensDTO(BaseDTO):
    access_token: str
    refresh_token: str


@dataclass(slots=True, frozen=True)
class SessionDTO(BaseDTO):
    session_id: str
    user_ip: str
    browser: str
    created_at: datetime.datetime


@dataclass(slots=True, frozen=True)
class RevokeSessionDTO(BaseDTO):
    access_token: str
    session_id: str


@dataclass(slots=True, frozen=True)
class ProfileDTO(BaseDTO):
    user_id: str
    username: str
    email: str
    registered_at: datetime.datetime
    verified: bool = False


@dataclass(slots=True, frozen=True)
class UpdateEmailDTO(BaseDTO):
    access_token: str
    new_email: str


@dataclass(slots=True, frozen=True)
class UpdatePasswordDTO(BaseDTO):
    access_token: str
    old_password: str
    new_password: str
