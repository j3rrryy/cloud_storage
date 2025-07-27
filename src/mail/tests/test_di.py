import os
from unittest.mock import call, patch

from aiokafka import AIOKafkaConsumer
from aiosmtplib import SMTP

from di import configure_inject, consumer_factory, setup_di, smtp_factory
from enums import MailTypes


@patch("di.di.SMTP")
def test_smtp_factory(mock_smtp):
    smtp = smtp_factory()
    mock_smtp.assert_called_once_with(
        hostname=os.environ["MAIL_HOSTNAME"],
        port=int(os.environ["MAIL_PORT"]),
        username=os.environ["MAIL_USERNAME"],
        password=os.environ["MAIL_PASSWORD"],
        use_tls=True,
        timeout=10,
    )
    assert smtp == mock_smtp.return_value


@patch("di.di.AIOKafkaConsumer")
def test_consumer_factory(mock_consumer):
    consumer = consumer_factory()
    mock_consumer.assert_called_once_with(
        MailTypes.VERIFICATION.name,
        MailTypes.INFO.name,
        MailTypes.RESET.name,
        bootstrap_servers=os.environ["KAFKA_SERVICE"],
        group_id="mail",
        auto_offset_reset="earliest",
        max_poll_records=1000,
        request_timeout_ms=10000,
    )
    assert consumer == mock_consumer.return_value


@patch("di.di.inject.Binder")
@patch("di.di.smtp_factory")
@patch("di.di.consumer_factory")
def test_configure_inject(mock_consumer_factory, mock_smtp_factory, mock_binder):
    configure_inject(mock_binder)

    expected_calls = [
        call(SMTP, mock_smtp_factory),
        call(AIOKafkaConsumer, mock_consumer_factory),
    ]

    mock_binder.bind_to_provider.assert_has_calls(expected_calls, any_order=True)
    assert mock_binder.bind_to_provider.call_count == 2


@patch("di.di.inject.configure")
@patch("di.di.configure_inject")
def test_setup_di(mock_configure_inject, mock_inject_configure):
    setup_di()
    mock_inject_configure.assert_called_once_with(mock_configure_inject, once=True)
