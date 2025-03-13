from unittest.mock import AsyncMock, patch

import grpc
import pytest

from config import load_config
from proto import AuthStub, FileStub
from service import (
    AuthService,
    FileService,
    MailService,
    connect_auth_service,
    connect_file_service,
    connect_mail_service,
)

config = load_config()


@pytest.mark.asyncio
@patch("service.connect.grpc.aio.insecure_channel")
async def test_connect_auth_service(mock_channel):
    mock_channel_instance = AsyncMock()
    mock_channel_instance.__aenter__.return_value = mock_channel_instance
    mock_channel.return_value = mock_channel_instance

    async for service in connect_auth_service():
        mock_channel.assert_called_once_with(
            config.app.auth_service, compression=grpc.Compression.Deflate
        )
        assert isinstance(service._stub, AuthStub)
        assert isinstance(service, AuthService)


@pytest.mark.asyncio
@patch("service.connect.grpc.aio.insecure_channel")
async def test_connect_file_service(mock_channel):
    mock_channel_instance = AsyncMock()
    mock_channel_instance.__aenter__.return_value = mock_channel_instance
    mock_channel.return_value = mock_channel_instance

    async for service in connect_file_service():
        mock_channel.assert_called_once_with(
            config.app.file_service, compression=grpc.Compression.Deflate
        )
        assert isinstance(service._stub, FileStub)
        assert isinstance(service, FileService)


@pytest.mark.asyncio
@patch("service.connect.AIOKafkaProducer")
async def test_connect_mail_service(mock_producer):
    mock_instance = AsyncMock()
    mock_producer.return_value = mock_instance
    mock_instance.__aenter__.return_value = mock_instance

    async for service in connect_mail_service():
        mock_producer.assert_called_once_with(
            bootstrap_servers=config.app.kafka_service, compression_type="lz4"
        )
        assert isinstance(service, MailService)
