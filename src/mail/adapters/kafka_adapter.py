from typing import Any, AsyncGenerator

import inject
import msgspec
import picologging as logging

from protocols import KafkaConsumerProtocol, MetricsCollectorProtocol

from .base_adapter import BaseKafkaAdapter


class KafkaAdapter(BaseKafkaAdapter, KafkaConsumerProtocol):
    logger = logging.getLogger()

    @inject.autoparams()
    async def consume_messages(
        self, metrics_collector: MetricsCollectorProtocol
    ) -> AsyncGenerator[tuple[str, dict[str, Any]], None]:
        async for message in self._consumer:
            if message.value is None:
                continue

            topic = message.topic
            with metrics_collector.record_processing_time():
                try:
                    decoded_message = msgspec.msgpack.decode(message.value, type=dict)
                    yield topic, decoded_message
                    metrics_collector.record_success(topic)
                except Exception as exc:
                    self.logger.exception(exc)
                    metrics_collector.record_failure(topic)
