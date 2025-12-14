from email.mime import multipart
from typing import Protocol


class SMTPClientProtocol(Protocol):
    async def send_mail(self, mail: multipart.MIMEMultipart) -> None: ...
