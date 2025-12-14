from protocols import ApplicationFacadeProtocol, KafkaFacadeProtocol, SMTPFacadeProtocol


class ApplicationFacade(ApplicationFacadeProtocol):
    def __init__(
        self, kafka_facade: KafkaFacadeProtocol, smtp_facade: SMTPFacadeProtocol
    ):
        self._kafka_facade = kafka_facade
        self._smtp_facade = smtp_facade

    async def start_processing(self) -> None:
        generator = await self._kafka_facade.consume_messages()
        async for dto in generator:
            await self._smtp_facade.send_mail(dto)
