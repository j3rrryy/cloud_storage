from email.mime import multipart
from typing import Protocol


class SMTPClientProtocol(Protocol):
    async def send_message(self, message: multipart.MIMEMultipart) -> None: ...
