import copy
from typing import Any

from litestar.logging import LoggingConfig
from uvicorn.config import LOGGING_CONFIG


def setup_litestar_logging() -> LoggingConfig:
    return LoggingConfig(
        root={"level": "INFO", "handlers": ["queue_listener"]},
        formatters={
            "standard": {"format": "%(asctime)s | %(levelname)s | %(message)s"}
        },
    )


def setup_uvicorn_logging() -> dict[str, Any]:
    config = copy.deepcopy(LOGGING_CONFIG)
    config["formatters"]["default"]["fmt"] = "%(asctime)s | %(levelname)s | %(message)s"
    config["formatters"]["access"]["fmt"] = (
        "%(asctime)s | %(levelname)s | %(request_line)s | %(status_code)s"
    )
    return config
