from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from factories import KafkaConsumerFactory


@pytest.mark.asyncio
async def test_kafka_consumer_factory_initialize_success():
    with (
        patch("factories.kafka_consumer_factory.AIOKafkaConsumer") as mock_consumer,
        patch("factories.kafka_consumer_factory.KafkaAdapter") as mock_adapter,
    ):
        factory = KafkaConsumerFactory()
        mock_consumer_instance = AsyncMock()
        mock_consumer_instance.start = AsyncMock()
        mock_consumer.return_value = mock_consumer_instance
        mock_adapter_instance = MagicMock()
        mock_adapter.return_value = mock_adapter_instance

        await factory.initialize()

        mock_consumer_instance.start.assert_awaited_once()
        assert factory._aiokafka_consumer == mock_consumer_instance
        assert factory._kafka_consumer == mock_adapter_instance


@pytest.mark.asyncio
async def test_kafka_consumer_factory_initialize_exception():
    factory = KafkaConsumerFactory()
    with (
        patch("factories.kafka_consumer_factory.AIOKafkaConsumer") as mock_consumer,
        patch.object(factory, "close", new_callable=AsyncMock) as mock_close,
    ):
        mock_consumer.return_value.start.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            await factory.initialize()

        mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_kafka_consumer_factory_close():
    factory = KafkaConsumerFactory()
    mock_consumer = AsyncMock()
    factory._aiokafka_consumer = mock_consumer

    await factory.close()

    mock_consumer.stop.assert_awaited_once()
    assert factory._aiokafka_consumer is None
    assert factory._kafka_consumer is None


@pytest.mark.asyncio
async def test_kafka_consumer_factory_close_no_aiokafka_consumer():
    factory = KafkaConsumerFactory()

    await factory.close()

    assert factory._aiokafka_consumer is None
    assert factory._kafka_consumer is None


def test_kafka_consumer_factory_get_kafka_consumer():
    factory = KafkaConsumerFactory()
    mock_consumer = MagicMock()
    factory._kafka_consumer = mock_consumer

    result = factory.get_kafka_consumer()

    assert result == mock_consumer


def test_kafka_consumer_factory_get_kafka_consumer_not_initialized():
    factory = KafkaConsumerFactory()

    with pytest.raises(RuntimeError, match="KafkaConsumer not initialized"):
        factory.get_kafka_consumer()
