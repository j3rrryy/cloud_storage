import asyncio
from email.mime import multipart

import picologging as logging
from aiosmtplib import SMTP, SMTPServerDisconnected

from protocols import SMTPClientProtocol
from settings import Settings


class SMTPAdapter(SMTPClientProtocol):
    logger = logging.getLogger()

    def __init__(self, smtp: SMTP):
        self._smtp = smtp
        self._retry_lock = asyncio.Lock()

    async def send_mail(self, mail: multipart.MIMEMultipart) -> None:
        for _ in range(Settings.RETRY_COUNT):
            try:
                await self._smtp.send_message(mail)
                return
            except SMTPServerDisconnected:
                async with self._retry_lock:
                    if not self._smtp.is_connected:
                        await self._reconnect()

        self.logger.error(f"Could not send mail after {Settings.RETRY_COUNT} attempts")

    async def _reconnect(self) -> None:
        await asyncio.sleep(Settings.RECONNECT_DELAY)
        self.logger.warning("Reconnecting to SMTP server...")
        await self._smtp.connect()
