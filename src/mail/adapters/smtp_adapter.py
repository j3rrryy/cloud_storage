from email.mime import multipart

from protocols import SMTPClientProtocol

from .base_adapter import BaseSMTPAdapter


class SMTPAdapter(BaseSMTPAdapter, SMTPClientProtocol):
    async def send_mail(self, mail: multipart.MIMEMultipart) -> None:
        await self._smtp.send_message(mail)
