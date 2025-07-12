from uvicorn.config import LOGGING_CONFIG

from config import setup_logging


def test_setup_logging():
    logging_config = setup_logging()

    assert logging_config.formatters == {
        "standard": {
            "format": "%(asctime)s | %(levelname)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    }

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
