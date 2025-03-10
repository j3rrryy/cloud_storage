import pytest
from grpc import StatusCode, aio
from litestar.exceptions import (
    HTTPException,
    InternalServerException,
    NotAuthorizedException,
    NotFoundException,
    PermissionDeniedException,
)

from services.base import RPCBase


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code, expected_exception",
    (
        (StatusCode.ALREADY_EXISTS, HTTPException),
        (StatusCode.UNAUTHENTICATED, NotAuthorizedException),
        (StatusCode.NOT_FOUND, NotFoundException),
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

    @RPCBase.handle_exception
    async def mock_function():
        raise exception

    with pytest.raises(expected_exception) as exc_info:
        await mock_function()

    assert exc_info.value.detail == DETAILS
