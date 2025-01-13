from dataclasses import dataclass

import picologging as logging
from cashews import cache
from environs import Env
from jwskate import Jwk
from uvicorn.config import LOGGING_CONFIG

__all__ = ["Config", "load_config"]


@dataclass(slots=True)
class AppConfig:
    name: str
    logger: logging.Logger
    public_key: Jwk
    private_key: Jwk


@dataclass(slots=True)
class PostgresConfig:
    driver: str
    user: str
    password: str
    host: str
    port: str
    database: str


@dataclass(slots=True)
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
        format="auth | %(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    LOGGING_CONFIG["formatters"]["default"].update(
        {
            "fmt": "auth | %(asctime)s | %(levelname)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    )
    LOGGING_CONFIG["formatters"]["access"].update(
        {
            "fmt": "auth | %(asctime)s | %(levelname)s | %(request_line)s | %(status_code)s",
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
        app=AppConfig(
            name=env("APP_NAME"),
            logger=logger,
            public_key=private_key.public_jwk(),
            private_key=private_key,
        ),
        postgres=PostgresConfig(
            driver=env("POSTGRES_DRIVER"),
            user=env("POSTGRES_USER"),
            password=env("POSTGRES_PASSWORD"),
            host=env("POSTGRES_HOST"),
            port=env("POSTGRES_PORT"),
            database=env("POSTGRES_DB"),
        ),
    )
