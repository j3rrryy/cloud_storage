from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from grpc import StatusCode

from utils import ExceptionHandler, utc_now_naive


@pytest.mark.asyncio
@patch("utils.utils.logger")
async def test_exception_handler_success(mock_logger):
    context = AsyncMock()

    async def mock_func():
        return "ok"

    res = await ExceptionHandler.handle(context, mock_func)

    assert res == "ok"
    mock_logger.error.assert_not_called()
    context.abort.assert_not_called()


@pytest.mark.asyncio
@patch("utils.utils.logger")
async def test_exception_handler_exception(mock_logger):
    context = AsyncMock()

    async def mock_func():
        raise Exception(StatusCode.UNKNOWN, "Test details")

    with pytest.raises(Exception) as exc_info:
        await ExceptionHandler.handle(context, mock_func)

    assert exc_info.value.args == (StatusCode.UNKNOWN, "Test details")
    mock_logger.error.assert_called_once_with(
        "Status code: UNKNOWN (2), details: Test details"
    )
    context.abort.assert_awaited_once_with(StatusCode.UNKNOWN, "Test details")


def test_utc_now_naive():
    now = utc_now_naive()

    assert isinstance(now, datetime)
    assert now.tzinfo is None
