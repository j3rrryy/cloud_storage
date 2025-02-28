from unittest.mock import MagicMock

import pytest
from litestar import Request
from litestar.exceptions import NotAuthorizedException

from utils import validate_access_token

from .mocks import ACCESS_TOKEN


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
