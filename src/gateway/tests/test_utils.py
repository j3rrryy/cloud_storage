from unittest.mock import MagicMock

import pytest
from litestar import MediaType, Request, Response
from litestar.exceptions import NotAuthorizedException

from utils import exception_handler, validate_access_token

from .mocks import ACCESS_TOKEN


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


@pytest.mark.parametrize(
    "header_value, expected_token, expected_exception, expected_message",
    [
        (f"Bearer {ACCESS_TOKEN}", ACCESS_TOKEN, None, None),
        (None, None, NotAuthorizedException, "Token is missing"),
        (
            f"Aearer {ACCESS_TOKEN}",
            None,
            NotAuthorizedException,
            "Invalid token format",
        ),
        ("Bearer", None, NotAuthorizedException, "Invalid token format"),
    ],
)
def test_validate_access_token(
    header_value, expected_token, expected_exception, expected_message
):
    mock_request = MagicMock(spec=Request)
    mock_request.headers.get.return_value = header_value

    if expected_exception and expected_message:
        with pytest.raises(expected_exception) as exc_info:
            validate_access_token(mock_request)

        assert expected_message in exc_info.value.detail
    else:
        token = validate_access_token(mock_request)

        assert token == expected_token
