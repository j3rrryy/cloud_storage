from unittest.mock import AsyncMock, MagicMock

import pytest
from grpc import StatusCode
from picologging import Logger

from utils import ExceptionHandler


@pytest.mark.asyncio
async def test_exception_handler_success():
    logger = MagicMock(spec=Logger)
    handler = ExceptionHandler(logger)
    context = AsyncMock()

    async def mock_func():
        return "ok"

    res = await handler(context, mock_func)

    assert res == "ok"
    logger.error.assert_not_called()
    context.abort.assert_not_called()


@pytest.mark.asyncio
async def test_exception_handler_exception():
    logger = MagicMock(spec=Logger)
    handler = ExceptionHandler(logger)
    context = AsyncMock()

    async def mock_func():
        raise Exception(StatusCode.UNKNOWN, "Test details")

    with pytest.raises(Exception) as exc_info:
        await handler(context, mock_func)

    assert exc_info.value.args == (StatusCode.UNKNOWN, "Test details")
    logger.error.assert_called_once_with(
        "Status code: UNKNOWN (2), details: Test details"
    )
    context.abort.assert_awaited_once_with(StatusCode.UNKNOWN, "Test details")
