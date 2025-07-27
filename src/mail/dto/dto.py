from dataclasses import dataclass

from .base import BaseMailDTO


@dataclass(slots=True, frozen=True)
class VerificationMailDTO(BaseMailDTO):
    verification_token: str


@dataclass(slots=True, frozen=True)
class InfoMailDTO(BaseMailDTO):
    user_ip: str
    browser: str


@dataclass(slots=True, frozen=True)
class ResetMailDTO(BaseMailDTO):
    code: str
