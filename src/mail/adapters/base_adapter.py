from aiokafka import AIOKafkaConsumer
from aiosmtplib import SMTP

from protocols import MetricsCollectorProtocol


class BaseKafkaAdapter:
    def __init__(
        self, consumer: AIOKafkaConsumer, metrics_collector: MetricsCollectorProtocol
    ):
        self._consumer = consumer
        self._metrics_collector = metrics_collector


class BaseSMTPAdapter:
    def __init__(self, client: SMTP):
        self._client = client
