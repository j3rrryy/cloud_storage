from aiokafka import AIOKafkaProducer

from adapters import MailKafkaAdapter
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

    def get_mail_service(self):
        if not self._mail_service:
            raise RuntimeError("MailService not initialized")
        return self._mail_service
