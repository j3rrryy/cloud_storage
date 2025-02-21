from unittest.mock import AsyncMock, patch

import grpc
import pytest

from config import load_config
from proto import AuthStub, FilesStub
from services import (
    Auth,
    Files,
    Mail,
    connect_auth_service,
    connect_files_service,
    connect_mail_service,
)

config = load_config()


@pytest.mark.asyncio
@patch("grpc.aio.insecure_channel")
async def test_connect_auth_service(mock_channel):
    mock_channel_instance = AsyncMock()
    mock_channel_instance.__aenter__.return_value = mock_channel_instance
    mock_channel.return_value = mock_channel_instance

    async for service in connect_auth_service():
        mock_channel.assert_called_once_with(
            config.app.auth_service, compression=grpc.Compression.Deflate
        )
        assert isinstance(service._stub, AuthStub)
        assert isinstance(service, Auth)


@pytest.mark.asyncio
@patch("grpc.aio.insecure_channel")
async def test_connect_files_service(mock_channel):
    mock_channel_instance = AsyncMock()
    mock_channel_instance.__aenter__.return_value = mock_channel_instance
    mock_channel.return_value = mock_channel_instance

    async for service in connect_files_service():
        mock_channel.assert_called_once_with(
            config.app.files_service, compression=grpc.Compression.Deflate
        )
        assert isinstance(service._stub, FilesStub)
        assert isinstance(service, Files)


@pytest.mark.asyncio
@patch("services.connect.AIOKafkaProducer")
async def test_connect_mail_service(mock_producer):
    mock_instance = AsyncMock()
    mock_producer.return_value = mock_instance
    mock_instance.__aenter__.return_value = mock_instance

    async for service in connect_mail_service():
        mock_producer.assert_called_once_with(
            bootstrap_servers=config.app.kafka_service, compression_type="lz4"
        )
        assert isinstance(service, Mail)
