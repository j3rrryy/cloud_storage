from dataclasses import dataclass

from .base import BaseRequestDTO, Model


@dataclass(slots=True, frozen=True)
class RegisterRequestDTO(BaseRequestDTO):
    username: str
    email: str
    password: str


@dataclass(slots=True, frozen=True)
class ResetCodeRequestDTO(BaseRequestDTO):
    user_id: str
    code: str


@dataclass(slots=True, frozen=True)
class ResetPasswordRequestDTO(BaseRequestDTO):
    user_id: str
    new_password: str


@dataclass(slots=True, frozen=True)
class LogInRequestDTO(BaseRequestDTO):
    username: str
    password: str
    user_ip: str
    user_agent: str


@dataclass(slots=True, frozen=True)
class LogInDataRequestDTO(BaseRequestDTO):
    access_token: str
    refresh_token: str
    user_id: str
    user_ip: str
    browser: str


@dataclass(slots=True, frozen=True)
class RefreshRequestDTO(BaseRequestDTO):
    refresh_token: str
    user_ip: str
    user_agent: str


@dataclass(slots=True, frozen=True)
class RefreshDataRequestDTO(BaseRequestDTO):
    access_token: str
    refresh_token: str
    old_refresh_token: str
    user_id: str
    user_ip: str
    browser: str

    def to_model(self, model: type[Model]) -> Model:
        return model(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            user_id=self.user_id,
            user_ip=self.user_ip,
            browser=self.browser,
        )


@dataclass(slots=True, frozen=True)
class RevokeSessionRequestDTO(BaseRequestDTO):
    access_token: str
    session_id: str


@dataclass(slots=True, frozen=True)
class UpdateEmailRequestDTO(BaseRequestDTO):
    access_token: str
    new_email: str


@dataclass(slots=True, frozen=True)
class UpdateEmailDataRequestDTO(BaseRequestDTO):
    user_id: str
    access_token: str
    new_email: str


@dataclass(slots=True, frozen=True)
class UpdatePasswordRequestDTO(BaseRequestDTO):
    access_token: str
    old_password: str
    new_password: str


@dataclass(slots=True, frozen=True)
class UpdatePasswordDataRequestDTO(BaseRequestDTO):
    user_id: str
    access_token: str
    old_password: str
    new_password: str
