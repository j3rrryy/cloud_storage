from typing import AsyncGenerator, Protocol

from dto import BaseMailDTO


class KafkaFacadeProtocol(Protocol):
    async def consume_messages(self) -> AsyncGenerator[BaseMailDTO, None]: ...
