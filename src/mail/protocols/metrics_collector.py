from typing import Protocol

from prometheus_client.context_managers import Timer


class MetricsCollectorProtocol(Protocol):
    @classmethod
    def record_success(cls, topic: str) -> None: ...

    @classmethod
    def record_failure(cls, topic: str) -> None: ...

    @classmethod
    def record_processing_time(cls) -> Timer: ...
