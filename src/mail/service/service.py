import pickle

from aiokafka import AIOKafkaConsumer

from config import load_config
from controllers import MailController as MC
from mail import get_smtp
from utils import MailTypes


class MailService:
    __slots__ = "_consumer"

    _logger = load_config().app.logger

    def __init__(self, consumer: AIOKafkaConsumer) -> None:
        self._consumer = consumer

    async def process_messages(self):
        async with self._consumer as consumer:
            async for message in consumer:
                async with get_smtp() as smtp:
                    try:
                        msg = pickle.loads(message.value)
                        await MC.send_email(msg, MailTypes[message.topic], smtp)
                        self._logger.info(
                            f"Sent {message.topic} mail to {msg['email']}"
                        )
                    except Exception as exc:
                        self._logger.error(str(exc))
