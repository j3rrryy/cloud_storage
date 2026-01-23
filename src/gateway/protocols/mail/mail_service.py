from typing import Protocol

from dto import mail_dto


class MailServiceProtocol(Protocol):
    async def email_confirmation(
        self, email_confirmation_mail: mail_dto.EmailConfirmationMailDTO
    ) -> None: ...

    async def new_login(self, new_login_mail: mail_dto.NewLoginMailDTO) -> None: ...

    async def password_reset(
        self, password_reset_mail: mail_dto.PasswordResetMailDTO
    ) -> None: ...
