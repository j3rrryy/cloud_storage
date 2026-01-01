import picologging as logging
from uvicorn.config import LOGGING_CONFIG


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
    )
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = (
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    LOGGING_CONFIG["formatters"]["access"]["fmt"] = (
        "%(asctime)s | %(levelname)s | %(request_line)s | %(status_code)s"
    )
