from dataclasses import dataclass

import picologging as logging
from environs import Env

__all__ = ["Config", "load_config"]


@dataclass(slots=True)
class AppConfig:
    name: str
    verification_url: str
    logger: logging.Logger
    kafka_service: str


@dataclass(slots=True)
class SMTPConfig:
    username: str
    password: str
    hostname: str
    port: int


@dataclass(slots=True)
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
        format="mail | %(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    return Config(
        app=AppConfig(
            name=env("APP_NAME"),
            verification_url=env("VERIFICATION_URL"),
            logger=logger,
            kafka_service=env("KAFKA_SERVICE"),
        ),
        smtp=SMTPConfig(
            username=env("MAIL_USERNAME"),
            password=env("MAIL_PASSWORD"),
            hostname=env("MAIL_HOSTNAME"),
            port=int(env("MAIL_PORT")),
        ),
    )
