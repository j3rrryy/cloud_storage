from aiokafka import AIOKafkaConsumer
from aiosmtplib import SMTP

from protocols import MetricsCollectorProtocol


class BaseKafkaAdapter:
    def __init__(
        self,
        consumer: AIOKafkaConsumer,
        metrics_collector: type[MetricsCollectorProtocol],
    ):
        self._consumer = consumer
        self._metrics_collector = metrics_collector


class BaseSMTPAdapter:
    def __init__(self, smtp: SMTP):
        self._smtp = smtp
