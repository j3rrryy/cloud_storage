from typing import Callable

from dto import (
    BaseMailDTO,
    EmailConfirmationMailDTO,
    NewLoginMailDTO,
    PasswordResetMailDTO,
)
from mail import MailRenderer
from protocols import SMTPClientProtocol, SMTPFacadeProtocol


class SMTPFacade(SMTPFacadeProtocol):
    _renderers: dict[type[BaseMailDTO], Callable] = {
        EmailConfirmationMailDTO: MailRenderer.email_confirmation,
        NewLoginMailDTO: MailRenderer.new_login,
        PasswordResetMailDTO: MailRenderer.password_reset,
    }

    def __init__(self, smtp_client: SMTPClientProtocol):
        self._smtp_client = smtp_client

    async def send_mail(self, dto: BaseMailDTO) -> None:
        dto_cls = type(dto)
        renderer = self._renderers.get(dto_cls)

        if not renderer:
            raise ValueError(f"No renderer found for {dto_cls.__name__}")

        mail = renderer(dto)
        await self._smtp_client.send_mail(mail)
