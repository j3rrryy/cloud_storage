import pickle

from aiokafka import AIOKafkaConsumer
from prometheus_client import Counter, Summary

from config import load_config
from controllers import MailController as MC
from mail import get_smtp
from utils import MailTypes


class MailService:
    __slots__ = "_consumer"

    _logger = load_config().app.logger

    email_sent_counter = Counter(
        "mail_service_emails_sent_total",
        "Total number of emails sent successfully",
        ["topic"],
    )
    email_failed_counter = Counter(
        "mail_service_emails_failed_total",
        "Total number of emails failed to send",
        ["topic"],
    )
    email_processing_time = Summary(
        "mail_service_email_processing_time_seconds",
        "Time spent processing email messages",
        ["topic"],
    )

    def __init__(self, consumer: AIOKafkaConsumer) -> None:
        self._consumer = consumer

    async def process_messages(self):
        async with self._consumer as consumer:
            async for message in consumer:
                async with get_smtp() as smtp:
                    with self.email_processing_time.labels(message.topic).time():
                        try:
                            msg = pickle.loads(message.value)
                            await MC.send_email(msg, MailTypes[message.topic], smtp)
                            self._logger.info(
                                f"Sent {message.topic} mail to {msg['email']}"
                            )
                            self.email_sent_counter.labels(message.topic).inc()
                        except Exception as exc:
                            self._logger.error(str(exc))
                            self.email_failed_counter.labels(message.topic).inc()
