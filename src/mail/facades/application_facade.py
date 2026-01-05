import asyncio
import logging

from protocols import ApplicationFacadeProtocol, KafkaFacadeProtocol, SMTPFacadeProtocol
from settings import Settings


class ApplicationFacade(ApplicationFacadeProtocol):
    logger = logging.getLogger()

    def __init__(
        self, kafka_facade: KafkaFacadeProtocol, smtp_facade: SMTPFacadeProtocol
    ):
        self._kafka_facade = kafka_facade
        self._smtp_facade = smtp_facade
        self._queue = asyncio.Queue(maxsize=Settings.QUEUE_SIZE)

    async def start_processing(self) -> None:
        reader = asyncio.create_task(self._reader())
        workers = [asyncio.create_task(self._worker()) for _ in range(Settings.WORKERS)]
        await asyncio.gather(reader, *workers, return_exceptions=True)

    async def _reader(self) -> None:
        async for dto in self._kafka_facade.consume_messages():
            await self._queue.put(dto)
        for _ in range(Settings.WORKERS):
            await self._queue.put(None)

    async def _worker(self) -> None:
        while dto := await self._queue.get():
            await self._smtp_facade.send_mail(dto)
            self.logger.info(
                f"Sent {dto.__class__.__name__.replace('MailDTO', '')} mail to {dto.email}"
            )
