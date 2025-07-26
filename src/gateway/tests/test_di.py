import os
from unittest.mock import AsyncMock, patch

import grpc
import pytest

from di.v1 import auth_service_factory, file_service_factory, mail_service_factory


@pytest.mark.asyncio
@patch("di.v1.di.grpc.aio.insecure_channel")
@patch("di.v1.di.AuthStub")
@patch("di.v1.di.AuthService")
async def test_auth_service_factory(
    mock_auth_service, mock_auth_stub, mock_insecure_channel
):
    mock_insecure_channel.return_value.__aenter__.return_value.channel_ready = (
        AsyncMock()
    )
    auth_service = await auth_service_factory().__anext__()

    mock_insecure_channel.assert_called_once_with(
        os.environ["AUTH_SERVICE"],
        options=[
            ("grpc.keepalive_time_ms", 60000),
            ("grpc.keepalive_timeout_ms", 10000),
            ("grpc.keepalive_permit_without_calls", 1),
        ],
        compression=grpc.Compression.Deflate,
    )
    mock_insecure_channel.return_value.__aenter__.return_value.channel_ready.assert_awaited_once()
    mock_auth_stub.assert_called_once_with(
        mock_insecure_channel.return_value.__aenter__.return_value
    )
    mock_auth_service.assert_called_once_with(mock_auth_stub.return_value)
    assert auth_service is mock_auth_service.return_value


@pytest.mark.asyncio
@patch("di.v1.di.grpc.aio.insecure_channel")
@patch("di.v1.di.FileStub")
@patch("di.v1.di.FileService")
async def test_file_service_factory(
    mock_file_service, mock_file_stub, mock_insecure_channel
):
    mock_insecure_channel.return_value.__aenter__.return_value.channel_ready = (
        AsyncMock()
    )
    file_service = await file_service_factory().__anext__()

    mock_insecure_channel.assert_called_once_with(
        os.environ["FILE_SERVICE"],
        options=[
            ("grpc.keepalive_time_ms", 60000),
            ("grpc.keepalive_timeout_ms", 10000),
            ("grpc.keepalive_permit_without_calls", 1),
        ],
        compression=grpc.Compression.Deflate,
    )
    mock_insecure_channel.return_value.__aenter__.return_value.channel_ready.assert_awaited_once()
    mock_file_stub.assert_called_once_with(
        mock_insecure_channel.return_value.__aenter__.return_value
    )
    mock_file_service.assert_called_once_with(mock_file_stub.return_value)
    assert file_service is mock_file_service.return_value


@pytest.mark.asyncio
@patch("di.v1.di.AIOKafkaProducer")
@patch("di.v1.di.MailService")
async def test_mail_service_factory(mock_mail_service, mock_producer):
    mail_service = await mail_service_factory().__anext__()

    mock_producer.assert_called_once_with(
        bootstrap_servers=os.environ["KAFKA_SERVICE"],
        compression_type="lz4",
        acks=1,
        linger_ms=10,
        request_timeout_ms=15000,
    )
    mock_mail_service.assert_called_once_with(
        mock_producer.return_value.__aenter__.return_value
    )
    assert mail_service is mock_mail_service.return_value
