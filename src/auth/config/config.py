from dataclasses import dataclass

import picologging as logging
from cashews import cache
from environs import Env
from jwskate import Jwk
from uvicorn.config import LOGGING_CONFIG

__all__ = ["Config", "load_config"]


@dataclass(slots=True, frozen=True)
class AppConfig:
    name: str
    logger: logging.Logger
    public_key: Jwk
    private_key: Jwk


@dataclass(slots=True, frozen=True)
class PostgresConfig:
    driver: str
    user: str
    password: str
    host: str
    port: str
    database: str


@dataclass(slots=True, frozen=True)
class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    app: AppConfig
    postgres: PostgresConfig


def load_config():
    env = Env()
    env.read_env()

    logger = logging.getLogger("auth")
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
    cache.setup(
        f"redis://{env('REDIS_USER')}:{env('REDIS_PASSWORD')}@"
        + f"{env('REDIS_HOST')}:{env('REDIS_PORT')}/{env('REDIS_DB')}",
        client_side=True,
    )
    private_key = Jwk.from_json(env("SECRET_KEY"))

    return Config(
        AppConfig(env("APP_NAME"), logger, private_key.public_jwk(), private_key),
        PostgresConfig(
            env("POSTGRES_DRIVER"),
            env("POSTGRES_USER"),
            env("POSTGRES_PASSWORD"),
            env("POSTGRES_HOST"),
            env("POSTGRES_PORT"),
            env("POSTGRES_DB"),
        ),
    )
