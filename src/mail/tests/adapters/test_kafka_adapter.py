from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.asyncio
@patch("adapters.kafka_adapter.msgspec.msgpack.decode")
async def test_consume_messages_empty_message(mock_decode, consumer, kafka_adapter):
    mock_message = MagicMock()
    mock_message.value = None
    consumer.__aiter__.return_value = iter([mock_message])

    async for _ in kafka_adapter.consume_messages():
        pass

    mock_decode.assert_not_called()
