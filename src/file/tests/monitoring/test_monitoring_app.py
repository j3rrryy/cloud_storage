from unittest.mock import AsyncMock, call

import pytest

from monitoring import MonitoringApp


@pytest.mark.asyncio
async def test_monitoring_app_scope_type_not_http():
    app = MonitoringApp(AsyncMock())
    mock_scope = {"type": "websocket", "path": "/metrics"}
    mock_send = AsyncMock()

    await app(mock_scope, AsyncMock(), mock_send)

    mock_send.assert_not_awaited()


@pytest.mark.asyncio
async def test_monitoring_app_metrics_path():
    app = MonitoringApp(AsyncMock())
    app._metrics_app = AsyncMock()
    mock_scope = {"type": "http", "path": "/metrics"}
    mock_receive = AsyncMock()
    mock_send = AsyncMock()

    await app(mock_scope, mock_receive, mock_send)

    app._metrics_app.assert_awaited_once_with(mock_scope, mock_receive, mock_send)


@pytest.mark.asyncio
async def test_monitoring_app_health_live_path():
    app = MonitoringApp(AsyncMock())
    mock_scope = {"type": "http", "path": "/health/live"}
    mock_send = AsyncMock()

    await app(mock_scope, AsyncMock(), mock_send)

    mock_send.assert_has_awaits(
        [
            call({"type": "http.response.start", "status": 200, "headers": []}),
            call({"type": "http.response.body", "body": b""}),
        ]
    )


@pytest.mark.asyncio
async def test_monitoring_app_health_ready_path_success():
    app = MonitoringApp(AsyncMock(return_value=True))
    mock_scope = {"type": "http", "path": "/health/ready"}
    mock_send = AsyncMock()

    await app(mock_scope, AsyncMock(), mock_send)

    mock_send.assert_has_awaits(
        [
            call({"type": "http.response.start", "status": 200, "headers": []}),
            call({"type": "http.response.body", "body": b""}),
        ]
    )


@pytest.mark.asyncio
async def test_monitoring_app_health_ready_path_fail():
    app = MonitoringApp(AsyncMock(return_value=False))
    mock_scope = {"type": "http", "path": "/health/ready"}
    mock_send = AsyncMock()

    await app(mock_scope, AsyncMock(), mock_send)

    mock_send.assert_has_awaits(
        [
            call({"type": "http.response.start", "status": 503, "headers": []}),
            call({"type": "http.response.body", "body": b""}),
        ]
    )


@pytest.mark.asyncio
async def test_monitoring_app_path_not_found():
    app = MonitoringApp(AsyncMock())
    mock_scope = {"type": "http", "path": "/test"}
    mock_send = AsyncMock()

    await app(mock_scope, AsyncMock(), mock_send)

    mock_send.assert_has_awaits(
        [
            call({"type": "http.response.start", "status": 404, "headers": []}),
            call({"type": "http.response.body", "body": b""}),
        ]
    )
