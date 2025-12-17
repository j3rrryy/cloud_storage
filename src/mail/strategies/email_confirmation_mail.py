from email.mime import multipart
from typing import cast

from dto import BaseMailDTO, EmailConfirmationMailDTO
from mail import MailRenderer
from protocols import MailStrategyProtocol


class EmailConfirmationMailStrategy(MailStrategyProtocol):
    @staticmethod
    def can_construct(dto: BaseMailDTO) -> bool:
        return isinstance(dto, EmailConfirmationMailDTO)

    @staticmethod
    def construct_mail(dto: BaseMailDTO) -> multipart.MIMEMultipart:
        dto = cast(EmailConfirmationMailDTO, dto)
        return MailRenderer.email_confirmation(dto)
