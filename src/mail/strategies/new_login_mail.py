from email.mime import multipart
from typing import cast

from dto import BaseMailDTO, NewLoginMailDTO
from mail import MailRenderer
from protocols import MailStrategyProtocol


class NewLoginMailStrategy(MailStrategyProtocol):
    @staticmethod
    def can_construct(dto: BaseMailDTO) -> bool:
        return isinstance(dto, NewLoginMailDTO)

    @staticmethod
    def construct_mail(dto: BaseMailDTO) -> multipart.MIMEMultipart:
        dto = cast(NewLoginMailDTO, dto)
        return MailRenderer.new_login(dto)
