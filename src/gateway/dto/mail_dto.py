from dataclasses import dataclass

from .base_dto import FromResponseMixin, ToMsgpackMixin


@dataclass(slots=True, frozen=True)
class VerificationMailDTO(FromResponseMixin, ToMsgpackMixin):
    verification_token: str
    username: str
    email: str


@dataclass(slots=True, frozen=True)
class InfoMailDTO(ToMsgpackMixin):
    username: str
    email: str
    user_ip: str
    browser: str


@dataclass(slots=True, frozen=True)
class ResetMailDTO(ToMsgpackMixin):
    code: str
    username: str
    email: str
