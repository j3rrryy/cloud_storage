from dataclasses import dataclass

from .base_dto import BaseMailDTO, FromResponseMixin, ToMsgpackMixin


@dataclass(slots=True, frozen=True)
class EmailConfirmationMailDTO(BaseMailDTO, FromResponseMixin, ToMsgpackMixin):
    token: str


@dataclass(slots=True, frozen=True)
class NewLoginMailDTO(BaseMailDTO, ToMsgpackMixin):
    user_ip: str
    browser: str


@dataclass(slots=True, frozen=True)
class PasswordResetMailDTO(BaseMailDTO, ToMsgpackMixin):
    code: str
