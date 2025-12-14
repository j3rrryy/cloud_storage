from typing import AsyncGenerator

from dto import BaseMailDTO, MessageToDTOConverter
from protocols import KafkaConsumerProtocol, KafkaFacadeProtocol


class KafkaFacade(KafkaFacadeProtocol):
    def __init__(self, kafka_consumer: KafkaConsumerProtocol):
        self._kafka_consumer = kafka_consumer

    async def consume_messages(self) -> AsyncGenerator[BaseMailDTO, None]:
        generator = await self._kafka_consumer.consume_messages()
        async for topic, message in generator:
            yield MessageToDTOConverter.convert(topic, message)
