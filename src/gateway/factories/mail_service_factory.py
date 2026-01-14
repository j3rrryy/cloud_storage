import asyncio

from aiokafka import AIOKafkaProducer

from adapters import MailKafkaAdapter
from protocols import MailServiceProtocol
from settings import Settings


class MailServiceFactory:
    def __init__(self):
        self._mail_producer = None
        self._mail_service = None

    async def initialize(self) -> None:
        try:
            await self._setup_mail_service()
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        if self._mail_producer is not None:
            try:
                await self._mail_producer.stop()
            finally:
                self._mail_producer = None
                self._mail_service = None

    async def _setup_mail_service(self) -> None:
        self._mail_producer = AIOKafkaProducer(
            bootstrap_servers=Settings.KAFKA_SERVICE,
            compression_type="lz4",
            acks=1,
            linger_ms=10,
        )
        await self._mail_producer.start()
        self._mail_service = MailKafkaAdapter(self._mail_producer)

    def get_mail_service(self) -> MailServiceProtocol:
        if not self._mail_service:
            raise RuntimeError("MailService not initialized")
        return self._mail_service

    async def is_ready(self) -> bool:
        if not self._mail_producer or not self._mail_service:
            return False
        for server in Settings.KAFKA_SERVICE.strip().split(","):
            host, port = server.split(":")
            try:
                async with asyncio.timeout(1):
                    _, writer = await asyncio.open_connection(host, port)
                    writer.close()
                    await writer.wait_closed()
                return True
            except Exception:
                pass
        return False
