from aiokafka import AIOKafkaConsumer
from aiosmtplib import SMTP


class BaseKafkaAdapter:
    def __init__(self, consumer: AIOKafkaConsumer):
        self._consumer = consumer


class BaseSMTPAdapter:
    def __init__(self, client: SMTP):
        self._client = client
