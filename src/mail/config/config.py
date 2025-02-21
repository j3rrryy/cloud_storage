from dataclasses import dataclass

import picologging as logging
from environs import Env
from uvicorn.config import LOGGING_CONFIG

__all__ = ["Config", "load_config"]


@dataclass(slots=True, frozen=True)
class AppConfig:
    name: str
    verification_url: str
    logger: logging.Logger
    kafka_service: str


@dataclass(slots=True, frozen=True)
class SMTPConfig:
    username: str
    password: str
    hostname: str
    port: int


@dataclass(slots=True, frozen=True)
class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    app: AppConfig
    smtp: SMTPConfig


def load_config():
    env = Env()
    env.read_env()

    logger = logging.getLogger("mail")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
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

    return Config(
        AppConfig(
            env("APP_NAME"), env("VERIFICATION_URL"), logger, env("KAFKA_SERVICE")
        ),
        SMTPConfig(
            env("MAIL_USERNAME"),
            env("MAIL_PASSWORD"),
            env("MAIL_HOSTNAME"),
            int(env("MAIL_PORT")),
        ),
    )
