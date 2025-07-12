from litestar.logging import LoggingConfig
from uvicorn.config import LOGGING_CONFIG


def setup_logging() -> LoggingConfig:
    LOGGING_CONFIG["formatters"]["default"].update(
        {
            "fmt": "%(asctime)s | %(levelname)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    )
    LOGGING_CONFIG["formatters"]["access"].update(
        {
            "fmt": "%(asctime)s | %(levelname)s | %(request_line)s | %(status_code)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    )
    return LoggingConfig(
        formatters={
            "standard": {
                "format": "%(asctime)s | %(levelname)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        }
    )
