import asyncio
import logging
from email.mime import multipart

from aiosmtplib import SMTP

from protocols import SMTPClientProtocol
from settings import Settings


class SMTPAdapter(SMTPClientProtocol):
    logger = logging.getLogger()

    def __init__(self, smtp: SMTP):
        self._smtp = smtp

    async def send_mail(self, mail: multipart.MIMEMultipart) -> None:
        delay = 1
        for attempt in range(1, Settings.RETRY_COUNT + 1):
            try:
                await self._smtp.send_message(mail)
                return
            except Exception as exc:
                self.logger.warning(f"Could not send mail at attempt #{attempt}: {exc}")
                if not self._smtp.is_connected:
                    await self._reconnect(delay)
                delay *= 2

        self.logger.error(f"Could not send mail after {Settings.RETRY_COUNT} attempts")
        raise RuntimeError("SMTP send failed")

    async def _reconnect(self, delay: int) -> None:
        await asyncio.sleep(delay)
        self.logger.warning("Reconnecting to SMTP server...")
        try:
            await self._smtp.connect()
        except Exception as exc:
            self.logger.warning(f"Could not reconnect to SMTP server: {exc}")
