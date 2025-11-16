from unittest.mock import MagicMock

from litestar import MediaType, Request, Response
from litestar.exceptions import NotAuthorizedException

from utils import exception_handler


def test_exception_handler():
    mock_request = MagicMock(spec=Request)
    mock_exception = NotAuthorizedException(
        detail="Token is missing", headers={"Test-Header": "Test Value"}
    )

    response = exception_handler(mock_request, mock_exception)

    assert isinstance(response, Response)
    assert response.content == {
        "status_code": mock_exception.status_code,
        "detail": mock_exception.detail,
    }
    assert response.headers == mock_exception.headers
    assert response.media_type == MediaType.MESSAGEPACK
    assert response.status_code == mock_exception.status_code
