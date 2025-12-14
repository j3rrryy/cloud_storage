from email.mime import multipart
from typing import Protocol

from dto import BaseMailDTO


class MailStrategyProtocol(Protocol):
    @staticmethod
    def can_construct(dto: BaseMailDTO) -> bool: ...

    @staticmethod
    def construct_mail(dto: BaseMailDTO) -> multipart.MIMEMultipart: ...
