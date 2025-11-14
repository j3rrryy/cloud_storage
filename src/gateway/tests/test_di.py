import os
from unittest.mock import AsyncMock, patch

import grpc
import pytest

from di.v1 import DIManager


@pytest.mark.asyncio
@patch("di.v1.di.DIManager._auth_channel")
@patch("di.v1.di.DIManager._file_channel")
@patch("di.v1.di.DIManager._mail_producer")
@patch("di.v1.di.DIManager.setup_auth_service")
@patch("di.v1.di.DIManager.setup_file_service")
@patch("di.v1.di.DIManager.setup_mail_service")
async def test_di_manager_lifespan(
    mock_setup_mail,
    mock_setup_file,
    mock_setup_auth,
    mock_mail_producer,
    mock_file_channel,
    mock_auth_channel,
):
    auth_close = AsyncMock()
    file_close = AsyncMock()
    mail_stop = AsyncMock()
    mock_auth_channel.close = auth_close
    mock_file_channel.close = file_close
    mock_mail_producer.stop = mail_stop

    await DIManager.setup()

    mock_setup_auth.assert_awaited_once()
    mock_setup_file.assert_awaited_once()
    mock_setup_mail.assert_awaited_once()
    assert DIManager._started

    await DIManager.close()

    auth_close.assert_awaited_once()
    file_close.assert_awaited_once()
    mail_stop.assert_awaited_once()
    assert not DIManager.auth_service
    assert not DIManager.file_service
    assert not DIManager.mail_service
    assert not DIManager._auth_channel
    assert not DIManager._file_channel
    assert not DIManager._mail_producer
    assert not DIManager._started


@pytest.mark.asyncio
@patch("di.v1.di.DIManager.setup_auth_service")
@patch("di.v1.di.DIManager.setup_file_service")
@patch("di.v1.di.DIManager.setup_mail_service")
async def test_di_manager_setup_already_started(
    mock_setup_mail, mock_setup_file, mock_setup_auth
):
    DIManager._started = True

    await DIManager.setup()

    mock_setup_auth.assert_not_awaited()
    mock_setup_file.assert_not_awaited()
    mock_setup_mail.assert_not_awaited()
    assert DIManager._started


@pytest.mark.asyncio
@patch("di.v1.di.DIManager.setup_auth_service")
@patch("di.v1.di.DIManager.close")
async def test_di_manager_setup_exception(mock_close, mock_setup_auth):
    DIManager._started = False
    mock_setup_auth.side_effect = Exception("Details")

    with pytest.raises(Exception):
        await DIManager.setup()

    mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_di_manager_close_already_closed():
    DIManager._auth_channel = None
    DIManager._file_channel = None
    DIManager._mail_producer = None

    await DIManager.close()

    assert not DIManager.auth_service
    assert not DIManager.file_service
    assert not DIManager.mail_service
    assert not DIManager._auth_channel
    assert not DIManager._file_channel
    assert not DIManager._mail_producer
    assert not DIManager._started


@pytest.mark.asyncio
@patch("di.v1.di.grpc.aio.insecure_channel")
@patch("di.v1.di.AuthStub")
@patch("di.v1.di.AuthService")
async def test_setup_auth_service(
    mock_auth_service, mock_auth_stub, mock_insecure_channel
):
    mock_insecure_channel.return_value.channel_ready = AsyncMock()

    await DIManager.setup_auth_service()

    mock_insecure_channel.assert_called_once_with(
        os.environ["AUTH_SERVICE"],
        options=[
            ("grpc.keepalive_time_ms", 60000),
            ("grpc.keepalive_timeout_ms", 10000),
            ("grpc.keepalive_permit_without_calls", 1),
        ],
        compression=grpc.Compression.Deflate,
    )
    mock_insecure_channel.return_value.channel_ready.assert_awaited_once()
    mock_auth_stub.assert_called_once_with(mock_insecure_channel.return_value)
    mock_auth_service.assert_called_once_with(mock_auth_stub.return_value)
    assert DIManager.auth_service == mock_auth_service.return_value
    assert DIManager._auth_channel == mock_insecure_channel.return_value


@pytest.mark.asyncio
@patch("di.v1.di.grpc.aio.insecure_channel")
@patch("di.v1.di.FileStub")
@patch("di.v1.di.FileService")
async def test_setup_file_service(
    mock_file_service, mock_file_stub, mock_insecure_channel
):
    mock_insecure_channel.return_value.channel_ready = AsyncMock()

    await DIManager.setup_file_service()

    mock_insecure_channel.assert_called_once_with(
        os.environ["FILE_SERVICE"],
        options=[
            ("grpc.keepalive_time_ms", 60000),
            ("grpc.keepalive_timeout_ms", 10000),
            ("grpc.keepalive_permit_without_calls", 1),
        ],
        compression=grpc.Compression.Deflate,
    )
    mock_insecure_channel.return_value.channel_ready.assert_awaited_once()
    mock_file_stub.assert_called_once_with(mock_insecure_channel.return_value)
    mock_file_service.assert_called_once_with(mock_file_stub.return_value)
    assert DIManager.file_service == mock_file_service.return_value
    assert DIManager._file_channel == mock_insecure_channel.return_value


@pytest.mark.asyncio
@patch("di.v1.di.AIOKafkaProducer")
@patch("di.v1.di.MailService")
async def test_setup_mail_service(mock_mail_service, mock_producer):
    mock_producer.return_value.start = AsyncMock()

    await DIManager.setup_mail_service()

    mock_producer.assert_called_once_with(
        bootstrap_servers=os.environ["KAFKA_SERVICE"],
        compression_type="lz4",
        acks=1,
        linger_ms=10,
        request_timeout_ms=10000,
    )
    mock_producer.return_value.start.assert_awaited_once()
    mock_mail_service.assert_called_once_with(mock_producer.return_value)
    assert DIManager.mail_service == mock_mail_service.return_value
    assert DIManager._mail_producer == mock_producer.return_value


@patch("di.v1.di.DIManager.auth_service")
def test_auth_service_factory(mock_auth_service):
    DIManager._started = True

    auth_service = DIManager.auth_service_factory()

    assert auth_service == mock_auth_service


def test_auth_service_factory_not_initialized():
    DIManager.auth_service = None

    with pytest.raises(Exception) as exc_info:
        DIManager.auth_service_factory()

    assert exc_info.errisinstance(RuntimeError)
    assert exc_info.value.args == (
        "AuthService not initialized; DIManager.setup() was not called",
    )


@patch("di.v1.di.DIManager.file_service")
def test_file_service_factory(mock_file_service):
    DIManager._started = True

    file_service = DIManager.file_service_factory()

    assert file_service == mock_file_service


def test_file_service_factory_not_initialized():
    DIManager.file_service = None

    with pytest.raises(Exception) as exc_info:
        DIManager.file_service_factory()

    assert exc_info.errisinstance(RuntimeError)
    assert exc_info.value.args == (
        "FileService not initialized; DIManager.setup() was not called",
    )


@patch("di.v1.di.DIManager.mail_service")
def test_mail_service_factory(mock_mail_service):
    DIManager._started = True

    mail_service = DIManager.mail_service_factory()

    assert mail_service == mock_mail_service


def test_mail_service_factory_not_initialized():
    DIManager.mail_service = None

    with pytest.raises(Exception) as exc_info:
        DIManager.mail_service_factory()

    assert exc_info.errisinstance(RuntimeError)
    assert exc_info.value.args == (
        "MailService not initialized; DIManager.setup() was not called",
    )
