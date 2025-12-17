from dataclasses import dataclass

from .base_dto import BaseMailDTO


@dataclass(slots=True, frozen=True)
class VerificationMailDTO(BaseMailDTO):
    verification_token: str


@dataclass(slots=True, frozen=True)
class LoginMailDTO(BaseMailDTO):
    user_ip: str
    browser: str


@dataclass(slots=True, frozen=True)
class ResetMailDTO(BaseMailDTO):
    code: str
