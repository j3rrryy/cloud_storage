from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import main


@pytest.mark.asyncio
@patch("main.connect_kafka_service")
@patch("main.MailService")
@patch("main.load_config")
async def test_start_mail_server(
    mock_load_config, mock_mail_service, mock_connect_kafka
):
    mock_logger = MagicMock()
    mock_load_config.return_value.app.logger = mock_logger

    mock_consumer = MagicMock()
    mock_connect_kafka.return_value = mock_consumer

    mock_service = AsyncMock()
    mock_mail_service.return_value = mock_service

    await main.start_mail_server()
    mock_connect_kafka.assert_called_once()
    mock_mail_service.assert_called_once_with(mock_consumer)
    mock_logger.info.assert_called_once_with("Server started")
    mock_service.process_messages.assert_awaited_once()


@pytest.mark.asyncio
@patch("main.make_asgi_app")
@patch("main.Config")
@patch("main.Server")
async def test_start_prometheus_server(mock_server, mock_config, mock_make_asgi_app):
    mock_app = MagicMock()
    mock_make_asgi_app.return_value = mock_app

    mock_config_instance = MagicMock()
    mock_config.return_value = mock_config_instance

    mock_server_instance = AsyncMock()
    mock_server.return_value = mock_server_instance

    await main.start_prometheus_server()
    mock_make_asgi_app.assert_called_once()
    mock_config.assert_called_once_with(
        app=mock_app, loop="uvloop", host="0.0.0.0", port=8000
    )
    mock_server.assert_called_once_with(mock_config_instance)
    mock_server_instance.serve.assert_awaited_once()


@pytest.mark.asyncio
@patch("main.start_mail_server")
@patch("main.start_prometheus_server")
async def test_main(mock_prometheus, mock_mail):
    mock_mail.return_value = None
    mock_prometheus.return_value = None

    await main.main()
    mock_mail.assert_awaited_once()
    mock_prometheus.assert_awaited_once()
