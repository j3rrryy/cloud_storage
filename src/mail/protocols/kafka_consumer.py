from typing import Any, AsyncGenerator, Protocol


class KafkaConsumerProtocol(Protocol):
    def consume_messages(self) -> AsyncGenerator[tuple[str, dict[str, Any]], None]: ...
