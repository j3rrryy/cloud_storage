from email.mime import multipart

from protocols import SMTPClientProtocol

from .base_adapter import BaseSMTPAdapter


class SMTPAdapter(BaseSMTPAdapter, SMTPClientProtocol):
    async def send_mail(self, mail: multipart.MIMEMultipart) -> None:
        await self._client.send_message(mail)
