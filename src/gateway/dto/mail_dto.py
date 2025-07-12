from dataclasses import dataclass

from .base_dto import BaseDTO


@dataclass(slots=True, frozen=True)
class VerificationMailDTO(BaseDTO):
    verification_token: str
    username: str
    email: str


@dataclass(slots=True, frozen=True)
class InfoMailDTO(BaseDTO):
    username: str
    email: str
    user_ip: str
    browser: str


@dataclass(slots=True, frozen=True)
class ResetMailDTO(BaseDTO):
    code: str
    username: str
    email: str
