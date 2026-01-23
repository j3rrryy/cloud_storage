import asyncio

from aiokafka import AIOKafkaConsumer

from adapters import KafkaAdapter
from enums import MailType
from protocols import KafkaConsumerProtocol
from settings import Settings


class KafkaConsumerFactory:
    def __init__(self):
        self._aiokafka_consumer = None
        self._kafka_consumer = None

    async def initialize(self) -> None:
        try:
            await self._setup_kafka_consumer()
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        if self._aiokafka_consumer is not None:
            try:
                await self._aiokafka_consumer.stop()
            finally:
                self._aiokafka_consumer = None
                self._kafka_consumer = None

    async def _setup_kafka_consumer(self) -> None:
        self._aiokafka_consumer = AIOKafkaConsumer(
            MailType.EMAIL_CONFIRMATION.name,
            MailType.NEW_LOGIN.name,
            MailType.PASSWORD_RESET.name,
            bootstrap_servers=Settings.KAFKA_SERVICE,
            group_id=Settings.KAFKA_GROUP_ID,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )
        await self._aiokafka_consumer.start()
        self._kafka_consumer = KafkaAdapter(self._aiokafka_consumer)

    def get_kafka_consumer(self) -> KafkaConsumerProtocol:
        if not self._kafka_consumer:
            raise RuntimeError("KafkaConsumer not initialized")
        return self._kafka_consumer

    async def is_ready(self) -> bool:
        if not self._aiokafka_consumer or not self._kafka_consumer:
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
