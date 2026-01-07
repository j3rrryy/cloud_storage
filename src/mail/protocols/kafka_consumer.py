from typing import Any, AsyncGenerator, Awaitable, Callable, Protocol

KafkaMessage = tuple[str, dict[str, Any], Callable[[], Awaitable[None]]]


class KafkaConsumerProtocol(Protocol):
    def consume_messages(self) -> AsyncGenerator[KafkaMessage, None]: ...
