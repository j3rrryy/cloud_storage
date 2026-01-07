from typing import AsyncGenerator, Awaitable, Callable, Protocol

from dto import BaseMailDTO

MailMessage = tuple[BaseMailDTO, Callable[[], Awaitable[None]]]


class KafkaFacadeProtocol(Protocol):
    def consume_messages(self) -> AsyncGenerator[MailMessage, None]: ...
