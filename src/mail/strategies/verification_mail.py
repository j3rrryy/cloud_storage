from email.mime import multipart
from typing import cast

from dto import BaseMailDTO, VerificationMailDTO
from mail import MailBuilder
from protocols import MailStrategyProtocol


class VerificationMailStrategy(MailStrategyProtocol):
    @staticmethod
    def can_construct(dto: BaseMailDTO) -> bool:
        return isinstance(dto, VerificationMailDTO)

    @staticmethod
    def construct_mail(dto: BaseMailDTO) -> multipart.MIMEMultipart:
        dto = cast(VerificationMailDTO, dto)
        return MailBuilder.verification(dto)
