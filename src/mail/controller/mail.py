from aiokafka import AIOKafkaConsumer
from prometheus_client import Counter, Summary

from config import load_config
from dto import DTOFactory
from mail import get_smtp
from service import MailService


class MailController:
    __slots__ = "_consumer"

    _logger = load_config().app.logger

    _email_sent_counter = Counter(
        "mail_service_emails_sent_total",
        "Total number of emails sent successfully",
        ["topic"],
    )
    _email_failed_counter = Counter(
        "mail_service_emails_failed_total",
        "Total number of emails failed to send",
        ["topic"],
    )
    _email_processing_time = Summary(
        "mail_service_email_processing_time_seconds",
        "Time spent processing email messages",
        ["topic"],
    )

    def __init__(self, consumer: AIOKafkaConsumer):
        self._consumer = consumer

    async def process_messages(self) -> None:
        async with self._consumer as consumer, get_smtp() as smtp:
            async for message in consumer:
                with self._email_processing_time.labels(message.topic).time():
                    try:
                        dto = DTOFactory.from_message(message)
                        await MailService.send_email(dto, smtp)
                        self._logger.info(f"Sent {message.topic} mail to {dto.email}")
                        self._email_sent_counter.labels(message.topic).inc()
                    except Exception as exc:
                        self._logger.error(exc)
                        self._email_failed_counter.labels(message.topic).inc()
