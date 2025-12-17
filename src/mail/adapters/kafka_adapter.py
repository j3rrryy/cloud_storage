from typing import Any, AsyncGenerator

import msgspec

from protocols import KafkaConsumerProtocol

from .base_adapter import BaseKafkaAdapter


class KafkaAdapter(BaseKafkaAdapter, KafkaConsumerProtocol):
    async def consume_messages(
        self,
    ) -> AsyncGenerator[tuple[str, dict[str, Any]], None]:
        async for message in self._consumer:
            if message.value is not None:
                topic = message.topic
                decoded_message = msgspec.msgpack.decode(message.value, type=dict)
                yield topic, decoded_message
