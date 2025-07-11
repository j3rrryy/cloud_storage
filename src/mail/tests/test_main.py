from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import main


@pytest.mark.asyncio
@patch("main.setup_di")
@patch("main.setup_logging")
@patch("main.logger")
@patch("main.MailController")
async def test_start_mail_server(
    mock_mail_controller, mock_logger, mock_setup_logging, mock_setup_di
):
    mock_mail_controller.process_messages = AsyncMock()

    await main.start_mail_server()
    mock_setup_di.assert_called_once()
    mock_setup_logging.assert_called_once()
    mock_logger.info.assert_called_once_with("Server started")
    mock_mail_controller.process_messages.assert_awaited_once()


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
    await main.main()
    mock_mail.assert_awaited_once()
    mock_prometheus.assert_awaited_once()
