from typing import AsyncGenerator

import msgspec
from aiokafka import AIOKafkaConsumer, TopicPartition

from protocols import KafkaConsumerProtocol, KafkaMessage


class KafkaAdapter(KafkaConsumerProtocol):
    def __init__(self, consumer: AIOKafkaConsumer):
        self._consumer = consumer

    async def consume_messages(self) -> AsyncGenerator[KafkaMessage, None]:
        async for message in self._consumer:
            tp = TopicPartition(message.topic, message.partition)

            async def commit(
                msg_tp=tp, msg_offset=message.offset, consumer=self._consumer
            ) -> None:
                await consumer.commit({msg_tp: msg_offset + 1})

            if message.value is None:
                await commit()
                continue

            decoded_message = msgspec.msgpack.decode(message.value, type=dict)
            yield message.topic, decoded_message, commit
