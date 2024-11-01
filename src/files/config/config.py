import logging
from asyncio import BoundedSemaphore
from dataclasses import dataclass

from cashews import cache
from environs import Env

__all__ = ["Config", "load_config"]


@dataclass(slots=True)
class AppConfig:
    logger: logging.Logger
    semaphore: BoundedSemaphore


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


def load_config() -> Config:
    env = Env()
    env.read_env()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s [%(asctime)s] %(message)s",
    )
    cache.setup(
        f"redis://{env("REDIS_USER")}:{env("REDIS_PASSWORD")}@" +
        f"{env("REDIS_HOST")}:{env("REDIS_PORT")}/{env("REDIS_DB")}",
        client_side=True,
    )

    return Config(
        app=AppConfig(
            logger=logging.getLogger(),
            semaphore=BoundedSemaphore(250),
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
