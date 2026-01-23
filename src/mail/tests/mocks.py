from unittest.mock import AsyncMock, MagicMock

import msgspec
from aiokafka import AIOKafkaConsumer
from aiosmtplib import SMTP

from enums import MailType

TOKEN = "eyJ0eXBlIjoyLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.1ukhU0OncZBofD_z3O5q5wrhoHaRm_RtAZAtqxI6CUY"
USERNAME = "test_username"
BROWSER = "Firefox 47.0, Windows 7"
USER_IP = "127.0.0.1"
EMAIL = "test@example.com"
CODE = "123456"


def create_consumer() -> AIOKafkaConsumer:
    mock_message = MagicMock()
    mock_message.topic = MailType.EMAIL_CONFIRMATION.name
    mock_message.value = msgspec.msgpack.encode(
        {"username": USERNAME, "email": EMAIL, "token": TOKEN}
    )

    consumer = AsyncMock(spec=AIOKafkaConsumer)
    consumer.__aiter__.return_value = iter([mock_message])
    return consumer


def create_smtp() -> SMTP:
    return AsyncMock(spec=SMTP)
