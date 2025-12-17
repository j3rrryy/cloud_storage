import pytest
from grpc import StatusCode, aio
from litestar.exceptions import (
    HTTPException,
    InternalServerException,
    NotAuthorizedException,
    NotFoundException,
    ServiceUnavailableException,
    ValidationException,
)

from adapters import BaseRPCAdapter


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code, expected_exception",
    (
        (StatusCode.ALREADY_EXISTS, HTTPException(status_code=409)),
        (StatusCode.UNAUTHENTICATED, NotAuthorizedException),
        (StatusCode.NOT_FOUND, NotFoundException),
        (StatusCode.INVALID_ARGUMENT, ValidationException),
        (StatusCode.RESOURCE_EXHAUSTED, ServiceUnavailableException),
        (StatusCode.UNAVAILABLE, ServiceUnavailableException),
        (StatusCode.INTERNAL, InternalServerException),
        (StatusCode.UNKNOWN, InternalServerException),
    ),
)
async def test_exception_handler(status_code, expected_exception):
    DETAILS = "Test error details"
    exception = aio.AioRpcError(
        code=status_code,
        initial_metadata=aio.Metadata(),
        trailing_metadata=aio.Metadata(),
        details=DETAILS,
    )

    @BaseRPCAdapter.exception_handler
    async def mock_function():
        raise exception

    with pytest.raises(HTTPException, match=DETAILS) as exc_info:
        await mock_function()

    assert exc_info.value.status_code == expected_exception.status_code
