from typing import Protocol

from prometheus_client.context_managers import Timer


class MetricsCollectorProtocol(Protocol):
    def record_success(self, topic: str) -> None: ...

    def record_failure(self, topic: str) -> None: ...

    def record_processing_time(self, topic: str) -> Timer: ...
