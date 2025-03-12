from dataclasses import dataclass

import picologging as logging
from cashews import cache
from environs import Env
from uvicorn.config import LOGGING_CONFIG

__all__ = ["Config", "load_config"]


@dataclass(slots=True, frozen=True)
class AppConfig:
    logger: logging.Logger


@dataclass(slots=True, frozen=True)
class PostgresConfig:
    driver: str
    user: str
    password: str
    host: str
    port: int
    database: str


@dataclass(slots=True, frozen=True)
class MinioConfig:
    access_key: str
    secret_key: str
    host: str
    port: str
    bucket: str


@dataclass(slots=True, frozen=True)
class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    app: AppConfig
    postgres: PostgresConfig
    minio: MinioConfig


def load_config():
    env = Env()
    env.read_env()

    logger = logging.getLogger("file")
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

    return Config(
        AppConfig(logger),
        PostgresConfig(
            env("POSTGRES_DRIVER"),
            env("POSTGRES_USER"),
            env("POSTGRES_PASSWORD"),
            env("POSTGRES_HOST"),
            int(env("POSTGRES_PORT")),
            env("POSTGRES_DB"),
        ),
        MinioConfig(
            env("MINIO_ROOT_USER"),
            env("MINIO_ROOT_PASSWORD"),
            env("MINIO_HOST"),
            env("MINIO_PORT"),
            env("MINIO_FILE_BUCKET"),
        ),
    )
