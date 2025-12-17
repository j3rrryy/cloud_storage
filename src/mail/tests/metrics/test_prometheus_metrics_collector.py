from enums import MailTypes
from metrics import PrometheusMetricsCollector


def test_record_success(mock_prometheus_metrics_collector):
    metrics_collector = mock_prometheus_metrics_collector
    topic = MailTypes.EMAIL_CONFIRMATION.name

    PrometheusMetricsCollector.record_success(topic)

    metrics_collector.sent_counter.labels.assert_called_once_with(topic)
    metrics_collector.failed_counter.labels.assert_not_called()
    metrics_collector.processing_time.time.assert_not_called()


def test_record_failure(mock_prometheus_metrics_collector):
    metrics_collector = mock_prometheus_metrics_collector
    topic = MailTypes.EMAIL_CONFIRMATION.name

    PrometheusMetricsCollector.record_failure(topic)

    metrics_collector.sent_counter.labels.assert_not_called()
    metrics_collector.failed_counter.labels.assert_called_once_with(topic)
    metrics_collector.processing_time.time.assert_not_called()


def test_record_processing_time(mock_prometheus_metrics_collector):
    metrics_collector = mock_prometheus_metrics_collector

    PrometheusMetricsCollector.record_processing_time()

    metrics_collector.sent_counter.labels.assert_not_called()
    metrics_collector.failed_counter.labels.assert_not_called()
    metrics_collector.processing_time.time.assert_called_once()
