from email.mime import multipart
from typing import cast

from dto import BaseMailDTO, LoginMailDTO
from mail import MailRenderer
from protocols import MailStrategyProtocol


class LoginMailStrategy(MailStrategyProtocol):
    @staticmethod
    def can_construct(dto: BaseMailDTO) -> bool:
        return isinstance(dto, LoginMailDTO)

    @staticmethod
    def construct_mail(dto: BaseMailDTO) -> multipart.MIMEMultipart:
        dto = cast(LoginMailDTO, dto)
        return MailRenderer.login(dto)
