from prometheus_client import Counter, Summary
from prometheus_client.context_managers import Timer

from protocols import MetricsCollectorProtocol


class PrometheusMetricsCollector(MetricsCollectorProtocol):
    _email_sent_counter = Counter(
        "mail_service_emails_sent_total",
        "Total number of emails sent successfully",
        ["topic"],
    )
    _email_failed_counter = Counter(
        "mail_service_emails_failed_total",
        "Total number of emails failed to send",
        ["topic"],
    )
    _email_processing_time = Summary(
        "mail_service_email_processing_time_seconds",
        "Time spent processing email messages",
        ["topic"],
    )

    def record_success(self, topic: str) -> None:
        self._email_sent_counter.labels(topic).inc()

    def record_failure(self, topic: str) -> None:
        self._email_failed_counter.labels(topic).inc()

    def record_processing_time(self, topic: str) -> Timer:
        return self._email_processing_time.labels(topic).time()
