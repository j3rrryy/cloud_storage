from config import setup_litestar_logging, setup_uvicorn_logging


def test_setup_litestar_logging():
    logging_config = setup_litestar_logging()

    assert logging_config.root == {"level": "INFO", "handlers": ["queue_listener"]}
    assert logging_config.formatters == {
        "standard": {"format": "%(asctime)s | %(levelname)s | %(message)s"}
    }


def test_setup_uvicorn_logging():
    logging_conifg = setup_uvicorn_logging()

    assert (
        logging_conifg["formatters"]["default"]["fmt"]
        == "%(asctime)s | %(levelname)s | %(message)s"
    )
    assert (
        logging_conifg["formatters"]["access"]["fmt"]
        == "%(asctime)s | %(levelname)s | %(request_line)s | %(status_code)s"
    )
