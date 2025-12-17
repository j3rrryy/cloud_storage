import asyncio
from email.mime import multipart

import picologging as logging
from aiosmtplib import SMTPServerDisconnected

from protocols import SMTPClientProtocol
from settings import Settings

from .base_adapter import BaseSMTPAdapter


class SMTPAdapter(BaseSMTPAdapter, SMTPClientProtocol):
    logger = logging.getLogger()

    async def send_mail(self, mail: multipart.MIMEMultipart) -> None:
        for _ in range(Settings.RETRY_COUNT):
            try:
                await self._smtp.send_message(mail)
                return
            except SMTPServerDisconnected:
                await self._reconnect()
        self.logger.error(f"Could not send mail after {Settings.RETRY_COUNT} attempts")

    async def _reconnect(self) -> None:
        await asyncio.sleep(Settings.RECONNECT_DELAY)
        self.logger.warning("Reconnecting to SMTP server...")
        await self._smtp.quit()
        await self._smtp.connect()
