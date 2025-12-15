from unittest.mock import AsyncMock, MagicMock

import msgspec
from aiokafka import AIOKafkaConsumer
from aiosmtplib import SMTP

from enums import MailTypes
from protocols import MetricsCollectorProtocol

VERIFICATION_TOKEN = "eyJ0eXBlIjoyLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.1ukhU0OncZBofD_z3O5q5wrhoHaRm_RtAZAtqxI6CUY"
USERNAME = "test_username"
BROWSER = "Firefox 47.0, Windows 7"
USER_IP = "127.0.0.1"
EMAIL = "test@example.com"
CODE = "123456"


def create_consumer() -> AIOKafkaConsumer:
    mock_message = MagicMock()
    mock_message.topic = MailTypes.VERIFICATION.name
    mock_message.value = msgspec.msgpack.encode(
        {"verification_token": VERIFICATION_TOKEN, "username": USERNAME, "email": EMAIL}
    )

    consumer = AsyncMock(spec=AIOKafkaConsumer)
    consumer.__aiter__.return_value = iter([mock_message])
    return consumer


def create_metrics_collector() -> type[MetricsCollectorProtocol]:
    class MockMetricsCollector(MetricsCollectorProtocol):
        record_success = MagicMock()
        record_failure = MagicMock()
        record_processing_time = MagicMock()

    return MockMetricsCollector


def create_smtp() -> SMTP:
    return AsyncMock(spec=SMTP)
