from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

import main
from settings import Settings


@pytest.mark.asyncio
async def test_start_mail_server():
    mock_application_facade = AsyncMock()

    await main.start_mail_server(mock_application_facade)

    mock_application_facade.start_processing.assert_awaited_once()


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
        app=mock_app,
        loop="uvloop",
        host=Settings.PROMETHEUS_SERVER_HOST,
        port=Settings.PROMETHEUS_SERVER_PORT,
        limit_concurrency=Settings.PROMETHEUS_SERVER_LIMIT_CONCURRENCY,
        limit_max_requests=Settings.PROMETHEUS_SERVER_LIMIT_MAX_REQUESTS,
    )
    mock_server.assert_called_once_with(mock_config_instance)
    mock_server_instance.serve.assert_awaited_once()


@pytest.mark.asyncio
@patch("main.setup_logging")
@patch("main.ServiceFactory")
@patch("main.start_mail_server")
@patch("main.start_prometheus_server")
@patch("main.logger")
async def test_main(
    mock_logger, mock_prometheus, mock_mail, mock_service_factory, mock_setup_logging
):
    mock_service_factory.return_value = AsyncMock()

    await main.main()

    mock_setup_logging.assert_called_once()
    mock_service_factory.assert_called_once()
    mock_service_factory.return_value.initialize.assert_awaited_once()
    mock_mail.assert_awaited_once()
    mock_prometheus.assert_awaited_once()
    mock_logger.info.assert_has_calls(
        [call("Mail server started"), call("Prometheus server started")]
    )


@pytest.mark.asyncio
@patch("main.setup_logging")
@patch("main.ServiceFactory")
@patch("main.start_mail_server")
@patch("main.start_prometheus_server")
@patch("main.logger")
@patch("main.asyncio.gather")
async def test_main_with_close(
    mock_gather,
    mock_logger,
    mock_prometheus,
    mock_mail,
    mock_service_factory,
    mock_setup_logging,
):
    mock_service_factory.return_value = AsyncMock()
    mock_gather.side_effect = Exception("Details")

    with pytest.raises(Exception):
        await main.main()

    mock_setup_logging.assert_called_once()
    mock_service_factory.assert_called_once()
    mock_service_factory.return_value.initialize.assert_awaited_once()
    mock_mail.assert_called_once()
    mock_prometheus.assert_called_once()
    mock_logger.info.assert_has_calls(
        [call("Mail server started"), call("Prometheus server started")]
    )
    mock_service_factory.return_value.close.assert_awaited_once()
