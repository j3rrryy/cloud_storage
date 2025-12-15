from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.asyncio
@patch("adapters.KafkaAdapter.logger")
async def test_consume_messages(mock_logger, kafka_adapter, metrics_collector):
    async for _ in kafka_adapter.consume_messages():
        pass

    metrics_collector.record_processing_time.assert_called_once()
    metrics_collector.record_success.assert_called_once()
    metrics_collector.record_failure.assert_not_called()
    mock_logger.exception.assert_not_called()


@pytest.mark.asyncio
@patch("adapters.KafkaAdapter.logger")
async def test_consume_messages_empty_message(
    mock_logger, consumer, kafka_adapter, metrics_collector
):
    mock_message = MagicMock()
    mock_message.value = None
    consumer.__aiter__.return_value = iter([mock_message])

    async for _ in kafka_adapter.consume_messages():
        pass

    metrics_collector.record_processing_time.assert_not_called()
    metrics_collector.record_success.assert_not_called()
    metrics_collector.record_failure.assert_not_called()
    mock_logger.exception.assert_not_called()


@pytest.mark.asyncio
@patch("msgspec.msgpack.decode")
@patch("adapters.KafkaAdapter.logger")
async def test_consume_messages_exception(
    mock_logger, mock_decode, kafka_adapter, metrics_collector
):
    exception = Exception("Details")
    mock_decode.side_effect = exception

    async for _ in kafka_adapter.consume_messages():
        pass

    metrics_collector.record_processing_time.assert_called_once()
    metrics_collector.record_success.assert_not_called()
    metrics_collector.record_failure.assert_called_once()
    mock_logger.exception.assert_called_once_with(exception)
