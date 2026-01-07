from typing import AsyncGenerator

from dto import MessageToDTOConverter
from protocols import KafkaConsumerProtocol, KafkaFacadeProtocol, MailMessage


class KafkaFacade(KafkaFacadeProtocol):
    def __init__(self, kafka_consumer: KafkaConsumerProtocol):
        self._kafka_consumer = kafka_consumer

    async def consume_messages(self) -> AsyncGenerator[MailMessage, None]:
        consumer = self._kafka_consumer.consume_messages()
        async for topic, message, commit in consumer:
            yield MessageToDTOConverter.convert(topic, message), commit
