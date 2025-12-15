from email.mime import multipart
from typing import cast

from dto import BaseMailDTO, InfoMailDTO
from mail import MailRenderer
from protocols import MailStrategyProtocol


class InfoMailStrategy(MailStrategyProtocol):
    @staticmethod
    def can_construct(dto: BaseMailDTO) -> bool:
        return isinstance(dto, InfoMailDTO)

    @staticmethod
    def construct_mail(dto: BaseMailDTO) -> multipart.MIMEMultipart:
        dto = cast(InfoMailDTO, dto)
        return MailRenderer.info(dto)
