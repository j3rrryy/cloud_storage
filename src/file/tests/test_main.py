from unittest.mock import ANY, AsyncMock, MagicMock, patch

import grpc
import pytest
from grpc_accesslog import AsyncAccessLogInterceptor, handlers
from py_async_grpc_prometheus.prometheus_async_server_interceptor import (
    PromAsyncServerInterceptor,
)

import main
from controller import FileServicer


@pytest.mark.asyncio
@patch("grpc.aio.server")
@patch("main.add_FileServicer_to_server")
@patch("main.load_config")
async def test_start_grpc_server(mock_load_config, mock_add_servicer, mock_grpc_server):
    mock_logger = MagicMock()
    mock_load_config.return_value.app.logger = mock_logger

    server_mock = MagicMock(spec=grpc.aio.Server)
    server_mock.add_insecure_port.return_value = None
    server_mock.start = AsyncMock()
    server_mock.wait_for_termination = AsyncMock()
    mock_grpc_server.return_value = server_mock

    await main.start_grpc_server()

    mock_grpc_server.assert_called_once_with(
        migration_thread_pool=ANY,
        interceptors=ANY,
        compression=grpc.Compression.Deflate,
    )
    _, kwargs = mock_grpc_server.call_args
    assert kwargs["migration_thread_pool"]._max_workers == 10
    assert len(kwargs["interceptors"]) == 2

    assert isinstance(kwargs["interceptors"][0], AsyncAccessLogInterceptor)
    assert kwargs["interceptors"][0]._logger == mock_logger
    assert kwargs["interceptors"][0]._handlers == [handlers.request]

    assert isinstance(kwargs["interceptors"][1], PromAsyncServerInterceptor)
    assert kwargs["interceptors"][1]._enable_handling_time_histogram

    args, _ = mock_add_servicer.call_args
    assert len(args) == 2
    assert isinstance(args[0], FileServicer)
    assert isinstance(args[1], grpc.aio.Server)

    server_mock.add_insecure_port.assert_called_once_with("[::]:50051")
    server_mock.start.assert_awaited_once()
    mock_logger.info.assert_called_once_with("gRPC server started")
    server_mock.wait_for_termination.assert_awaited_once()


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
@patch("main.start_grpc_server")
@patch("main.start_prometheus_server")
async def test_main(mock_prometheus, mock_grpc):
    mock_grpc.return_value = None
    mock_prometheus.return_value = None
    await main.main()

    mock_grpc.assert_awaited_once()
    mock_prometheus.assert_awaited_once()
