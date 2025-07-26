import pytest
from grpc import StatusCode, aio
from litestar.exceptions import (
    HTTPException,
    InternalServerException,
    NotAuthorizedException,
    NotFoundException,
    ServiceUnavailableException,
)

from service.v1 import RPCBaseService


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code, expected_exception",
    (
        (StatusCode.ALREADY_EXISTS, HTTPException),
        (StatusCode.UNAUTHENTICATED, NotAuthorizedException),
        (StatusCode.NOT_FOUND, NotFoundException),
        (StatusCode.RESOURCE_EXHAUSTED, ServiceUnavailableException),
        (StatusCode.INTERNAL, InternalServerException),
        (StatusCode.UNAVAILABLE, InternalServerException),
        (StatusCode.UNKNOWN, InternalServerException),
    ),
)
async def test_handle_exception(status_code, expected_exception):
    DETAILS = "Test error details"
    exception = aio.AioRpcError(
        code=status_code,
        initial_metadata=aio.Metadata(),
        trailing_metadata=aio.Metadata(),
        details=DETAILS,
    )

    @RPCBaseService.exception_handler
    async def mock_function():
        raise exception

    with pytest.raises(expected_exception) as exc_info:
        await mock_function()

    assert exc_info.value.detail == DETAILS
