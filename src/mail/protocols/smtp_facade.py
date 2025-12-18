from typing import Protocol

from dto import BaseMailDTO


class SMTPFacadeProtocol(Protocol):
    async def send_mail(self, dto: BaseMailDTO) -> None: ...
