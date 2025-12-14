from prometheus_client import Counter, Summary
from prometheus_client.context_managers import Timer

from protocols import MetricsCollectorProtocol


class PrometheusMetricsCollector(MetricsCollectorProtocol):
    _mails_sent_counter = Counter(
        "mail_service_mails_sent_total",
        "Total number of mails sent successfully",
        ["topic"],
    )
    _mails_failed_counter = Counter(
        "mail_service_mails_failed_total",
        "Total number of mails failed to send",
        ["topic"],
    )
    _mails_processing_time = Summary(
        "mail_service_mails_processing_time_seconds",
        "Time spent processing mails",
    )

    @classmethod
    def record_success(cls, topic: str) -> None:
        cls._mails_sent_counter.labels(topic).inc()

    @classmethod
    def record_failure(cls, topic: str) -> None:
        cls._mails_failed_counter.labels(topic).inc()

    @classmethod
    def record_processing_time(cls) -> Timer:
        return cls._mails_processing_time.time()
