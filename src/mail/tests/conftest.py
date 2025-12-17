from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from aiokafka import AIOKafkaConsumer
from aiosmtplib import SMTP

from adapters import KafkaAdapter, SMTPAdapter
from facades import ApplicationFacade, KafkaFacade, SMTPFacade
from metrics import PrometheusMetricsCollector
from protocols import (
    ApplicationFacadeProtocol,
    KafkaConsumerProtocol,
    KafkaFacadeProtocol,
    MetricsCollectorProtocol,
    SMTPClientProtocol,
    SMTPFacadeProtocol,
)

from .mocks import create_consumer, create_metrics_collector, create_smtp


@pytest.fixture
def consumer() -> AIOKafkaConsumer:
    return create_consumer()


@pytest.fixture
def metrics_collector() -> type[MetricsCollectorProtocol]:
    return create_metrics_collector()


@pytest.fixture
def smtp() -> SMTP:
    return create_smtp()


@pytest.fixture
def kafka_adapter(consumer, metrics_collector) -> KafkaConsumerProtocol:
    return KafkaAdapter(consumer, metrics_collector)


@pytest.fixture
def smtp_adapter(smtp) -> SMTPClientProtocol:
    return SMTPAdapter(smtp)


@pytest.fixture
def kafka_facade(kafka_adapter) -> KafkaFacadeProtocol:
    return KafkaFacade(kafka_adapter)


@pytest.fixture
def smtp_facade(smtp_adapter) -> SMTPFacadeProtocol:
    return SMTPFacade(smtp_adapter)


@pytest.fixture
def application_facade(kafka_facade, smtp_facade) -> ApplicationFacadeProtocol:
    return ApplicationFacade(kafka_facade, smtp_facade)


@pytest.fixture
def mock_prometheus_metrics_collector() -> Generator[type[object], None, None]:
    class MockPrometheusMetricsCollector:
        sent_counter = MagicMock()
        failed_counter = MagicMock()
        processing_time = MagicMock()

    with (
        patch.object(
            PrometheusMetricsCollector,
            "_mails_sent_counter",
            MockPrometheusMetricsCollector.sent_counter,
        ),
        patch.object(
            PrometheusMetricsCollector,
            "_mails_failed_counter",
            MockPrometheusMetricsCollector.failed_counter,
        ),
        patch.object(
            PrometheusMetricsCollector,
            "_mails_processing_time",
            MockPrometheusMetricsCollector.processing_time,
        ),
    ):
        yield MockPrometheusMetricsCollector
