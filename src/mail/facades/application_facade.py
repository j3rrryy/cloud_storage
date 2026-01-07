import logging

from protocols import ApplicationFacadeProtocol, KafkaFacadeProtocol, SMTPFacadeProtocol


class ApplicationFacade(ApplicationFacadeProtocol):
    logger = logging.getLogger()

    def __init__(
        self, kafka_facade: KafkaFacadeProtocol, smtp_facade: SMTPFacadeProtocol
    ):
        self._kafka_facade = kafka_facade
        self._smtp_facade = smtp_facade

    async def start_processing(self) -> None:
        async for dto, commit in self._kafka_facade.consume_messages():
            await self._smtp_facade.send_mail(dto)
            await commit()
            self.logger.info(
                f"Sent {dto.__class__.__name__.replace('MailDTO', '')} mail to {dto.email}"
            )
