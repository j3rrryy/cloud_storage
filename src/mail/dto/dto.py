from dataclasses import dataclass

from .base_dto import BaseMailDTO


@dataclass(slots=True, frozen=True)
class EmailConfirmationMailDTO(BaseMailDTO):
    token: str


@dataclass(slots=True, frozen=True)
class NewLoginMailDTO(BaseMailDTO):
    user_ip: str
    browser: str


@dataclass(slots=True, frozen=True)
class PasswordResetMailDTO(BaseMailDTO):
    code: str
