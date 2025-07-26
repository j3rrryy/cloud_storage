import inject
import picologging as logging
from aiokafka import AIOKafkaConsumer
from prometheus_client import Counter, Summary

from dto import DTOFactory
from service import MailService


class MailController:
    _logger = logging.getLogger()

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

    @classmethod
    @inject.autoparams()
    async def process_messages(cls, consumer: AIOKafkaConsumer) -> None:
        async with consumer:
            async for message in consumer:
                with cls._email_processing_time.labels(message.topic).time():
                    try:
                        dto = DTOFactory.from_message(message)
                        await MailService.send_email(dto)
                        cls._logger.info(f"Sent {message.topic} mail to {dto.email}")
                        cls._email_sent_counter.labels(message.topic).inc()
                    except Exception as exc:
                        cls._logger.exception(exc)
                        cls._email_failed_counter.labels(message.topic).inc()
