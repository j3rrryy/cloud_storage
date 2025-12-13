import inject
import picologging as logging
from aiokafka import AIOKafkaConsumer

from dto import DTOFactory
from protocols import MetricsCollectorProtocol
from service import MailService


class MailController:
    logger = logging.getLogger()

    @classmethod
    @inject.autoparams()
    async def process_messages(
        cls, consumer: AIOKafkaConsumer, metrics_collector: MetricsCollectorProtocol
    ) -> None:
        async for message in consumer:
            with metrics_collector.record_processing_time(message.topic):
                try:
                    dto = DTOFactory.from_message(message)
                    await MailService.send_email(dto)  # type: ignore
                    cls.logger.info(f"Sent {message.topic} mail to {dto.email}")
                    metrics_collector.record_success(message.topic)
                except Exception as exc:
                    cls.logger.exception(exc)
                    metrics_collector.record_failure(message.topic)
