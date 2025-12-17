from email.mime import multipart
from typing import cast

from dto import BaseMailDTO, PasswordResetMailDTO
from mail import MailRenderer
from protocols import MailStrategyProtocol


class PasswordResetMailStrategy(MailStrategyProtocol):
    @staticmethod
    def can_construct(dto: BaseMailDTO) -> bool:
        return isinstance(dto, PasswordResetMailDTO)

    @staticmethod
    def construct_mail(dto: BaseMailDTO) -> multipart.MIMEMultipart:
        dto = cast(PasswordResetMailDTO, dto)
        return MailRenderer.password_reset(dto)
