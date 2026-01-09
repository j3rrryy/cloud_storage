import asyncio
from typing import Awaitable, Callable

from facades import ApplicationFacade, KafkaFacade, SMTPFacade
from protocols import (
    ApplicationFacadeProtocol,
    KafkaConsumerProtocol,
    SMTPClientProtocol,
)

from .kafka_consumer_factory import KafkaConsumerFactory
from .smtp_client_factory import SMTPClientFactory


class ServiceFactory:
    def __init__(self):
        self._kafka_consumer_factory = KafkaConsumerFactory()
        self._smtp_client_factory = SMTPClientFactory()
        self._application_facade = None

    async def initialize(self) -> None:
        try:
            await asyncio.gather(
                self._kafka_consumer_factory.initialize(),
                self._smtp_client_factory.initialize(),
            )
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        await asyncio.gather(
            self._kafka_consumer_factory.close(),
            self._smtp_client_factory.close(),
            return_exceptions=True,
        )

    def get_kafka_consumer(self) -> KafkaConsumerProtocol:
        return self._kafka_consumer_factory.get_kafka_consumer()

    def get_smtp_client(self) -> SMTPClientProtocol:
        return self._smtp_client_factory.get_smtp_client()

    def get_application_facade(self) -> ApplicationFacadeProtocol:
        if not self._application_facade:
            kafka_facade = KafkaFacade(self.get_kafka_consumer())
            smtp_facade = SMTPFacade(self.get_smtp_client())
            self._application_facade = ApplicationFacade(kafka_facade, smtp_facade)
        return self._application_facade

    def get_is_ready(self) -> Callable[[], Awaitable[bool]]:
        async def is_ready() -> bool:
            kafka_ready = await self._kafka_consumer_factory.is_ready()
            smtp_ready = self._smtp_client_factory.is_ready()
            return kafka_ready and smtp_ready

        return is_ready
