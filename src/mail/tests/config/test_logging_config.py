from unittest.mock import patch

import picologging as logging
from uvicorn.config import LOGGING_CONFIG

from config import setup_logging


@patch("config.logging_config.logging.basicConfig")
def test_setup_logging(mock_basic_config):
    setup_logging()

    mock_basic_config.assert_called_once_with(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    assert (
        LOGGING_CONFIG["formatters"]["default"]["fmt"]
        == "%(asctime)s | %(levelname)s | %(message)s"
    )
    assert LOGGING_CONFIG["formatters"]["default"]["datefmt"] == "%Y-%m-%d %H:%M:%S"
    assert (
        LOGGING_CONFIG["formatters"]["access"]["fmt"]
        == "%(asctime)s | %(levelname)s | %(request_line)s | %(status_code)s"
    )
    assert LOGGING_CONFIG["formatters"]["access"]["datefmt"] == "%Y-%m-%d %H:%M:%S"
