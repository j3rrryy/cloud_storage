import datetime
from dataclasses import dataclass

from .base import BaseResponseDTO


@dataclass(slots=True, frozen=True)
class VerificationMailResponseDTO(BaseResponseDTO):
    verification_token: str
    username: str
    email: str


@dataclass(slots=True, frozen=True)
class ResetCodeResponseDTO(BaseResponseDTO):
    user_id: str
    username: str
    code: str


@dataclass(slots=True, frozen=True)
class LogInResponseDTO(BaseResponseDTO):
    access_token: str
    refresh_token: str
    email: str
    browser: str
    verified: bool


@dataclass(slots=True, frozen=True)
class AuthResponseDTO(BaseResponseDTO):
    user_id: str
    verified: bool


@dataclass(slots=True, frozen=True)
class RefreshResponseDTO(BaseResponseDTO):
    access_token: str
    refresh_token: str


@dataclass(slots=True, frozen=True)
class SessionInfoResponseDTO(BaseResponseDTO):
    session_id: str
    user_id: str | None
    access_token: str | None
    refresh_token: str | None
    user_ip: str
    browser: str
    last_accessed: datetime.datetime


@dataclass(slots=True, frozen=True)
class ProfileResponseDTO(BaseResponseDTO):
    user_id: str
    username: str
    email: str
    password: str | None
    verified: bool
    registered: datetime.datetime
