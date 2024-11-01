import logging
from dataclasses import dataclass

from cashews import cache
from environs import Env
from jwskate import Jwk

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


def load_config() -> Config:
    env = Env()
    env.read_env()
    private_key = Jwk.from_json(env("SECRET_KEY"))

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
            name=env("APP_NAME"),
            logger=logging.getLogger(),
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
