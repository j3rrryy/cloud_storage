from email.mime import multipart
from typing import cast

from dto import BaseMailDTO, ResetMailDTO
from factories import MailFactory
from protocols import MailStrategyProtocol


class ResetMailStrategy(MailStrategyProtocol):
    @staticmethod
    def can_construct(dto: BaseMailDTO) -> bool:
        return isinstance(dto, ResetMailDTO)

    @staticmethod
    def construct_mail(dto: BaseMailDTO) -> multipart.MIMEMultipart:
        dto = cast(ResetMailDTO, dto)
        return MailFactory.reset(dto)
