from aiosmtplib import SMTP

from adapters import SMTPAdapter
from protocols import SMTPClientProtocol
from settings import Settings


class SMTPClientFactory:
    def __init__(self):
        self._smtp = None
        self._smtp_client = None

    async def initialize(self) -> None:
        try:
            await self._setup_smtp_client()
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        if self._smtp is not None:
            try:
                await self._smtp.quit()
            finally:
                self._smtp = None
                self._smtp_client = None

    async def _setup_smtp_client(self) -> None:
        self._smtp = SMTP(
            username=Settings.MAIL_USERNAME,
            password=Settings.MAIL_PASSWORD,
            hostname=Settings.MAIL_HOSTNAME,
            port=Settings.MAIL_PORT,
            use_tls=Settings.MAIL_TLS,
        )
        await self._smtp.connect()
        self._smtp_client = SMTPAdapter(self._smtp)

    def get_smtp_client(self) -> SMTPClientProtocol:
        if not self._smtp_client:
            raise RuntimeError("SMTPClient not initialized")
        return self._smtp_client

    def is_ready(self) -> bool:
        if self._smtp and self._smtp_client:
            return True
        return False
