from typing import AsyncGenerator, Protocol

from dto import BaseMailDTO


class KafkaFacadeProtocol(Protocol):
    def consume_messages(self) -> AsyncGenerator[BaseMailDTO, None]: ...
