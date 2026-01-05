from typing import Protocol

from dto import request as request_dto
from dto import response as response_dto


class AuthServiceProtocol(Protocol):
    async def register(self, data: request_dto.RegisterRequestDTO) -> str: ...

    async def confirm_email(self, token: str) -> None: ...

    async def request_reset_code(
        self, email: str
    ) -> response_dto.ResetCodeResponseDTO: ...

    async def validate_reset_code(
        self, data: request_dto.ResetCodeRequestDTO
    ) -> bool: ...

    async def reset_password(
        self, data: request_dto.ResetPasswordRequestDTO
    ) -> None: ...

    async def log_in(
        self, data: request_dto.LogInRequestDTO
    ) -> response_dto.LogInResponseDTO: ...

    async def log_out(self, access_token: str) -> None: ...

    async def resend_email_confirmation_mail(
        self, access_token: str
    ) -> response_dto.EmailConfirmationMailResponseDTO: ...

    async def auth(self, access_token: str) -> str: ...

    async def refresh(
        self, data: request_dto.RefreshRequestDTO
    ) -> response_dto.RefreshResponseDTO: ...

    async def session_list(
        self, access_token: str
    ) -> list[response_dto.SessionInfoResponseDTO]: ...

    async def revoke_session(
        self, data: request_dto.RevokeSessionRequestDTO
    ) -> None: ...

    async def profile(self, access_token: str) -> response_dto.ProfileResponseDTO: ...

    async def update_email(
        self, data: request_dto.UpdateEmailRequestDTO
    ) -> response_dto.EmailConfirmationMailResponseDTO: ...

    async def update_password(
        self, data: request_dto.UpdatePasswordRequestDTO
    ) -> None: ...

    async def delete_profile(self, access_token: str) -> str: ...
