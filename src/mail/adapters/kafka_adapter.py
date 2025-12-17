from typing import Any, AsyncGenerator

import msgspec
from aiokafka import AIOKafkaConsumer

from protocols import KafkaConsumerProtocol


class KafkaAdapter(KafkaConsumerProtocol):
    def __init__(self, consumer: AIOKafkaConsumer):
        self._consumer = consumer

    async def consume_messages(
        self,
    ) -> AsyncGenerator[tuple[str, dict[str, Any]], None]:
        async for message in self._consumer:
            if message.value is not None:
                topic = message.topic
                decoded_message = msgspec.msgpack.decode(message.value, type=dict)
                yield topic, decoded_message
