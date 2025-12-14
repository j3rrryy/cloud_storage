from aiokafka import AIOKafkaConsumer

from adapters import KafkaAdapter
from enums import MailTypes
from metrics import PrometheusMetricsCollector
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
            MailTypes.VERIFICATION.name,
            MailTypes.INFO.name,
            MailTypes.RESET.name,
            bootstrap_servers=Settings.KAFKA_SERVICE,
            group_id=Settings.KAFKA_GROUP_ID,
            auto_offset_reset="earliest",
        )
        await self._aiokafka_consumer.start()
        self._kafka_consumer = KafkaAdapter(
            self._aiokafka_consumer, PrometheusMetricsCollector
        )

    def get_kafka_consumer(self) -> KafkaConsumerProtocol:
        if not self._kafka_consumer:
            raise RuntimeError("KafkaConsumer not initialized")
        return self._kafka_consumer
