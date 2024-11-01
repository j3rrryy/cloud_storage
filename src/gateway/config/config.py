from dataclasses import dataclass

from environs import Env
from litestar.config.cors import CORSConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin

__all__ = ["Config", "load_config"]


@dataclass(slots=True)
class AppConfig:
    debug: bool
    cors_config: CORSConfig
    openapi_config: OpenAPIConfig
    auth_service: str
    files_service: str
    kafka_service: str


@dataclass(slots=True)
class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    app: AppConfig


def load_config() -> Config:
    env = Env()
    env.read_env()

    cors_config = CORSConfig(
        allow_origins=env("ALLOWED_ORIGINS").split(", "),
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    openapi_config = OpenAPIConfig(
        path="/docs",
        title=env("APP_NAME"),
        version=env("VERSION"),
        render_plugins=(SwaggerRenderPlugin(),),
        security=[{"BearerToken": []}],
    )

    return Config(
        app=AppConfig(
            debug=bool(int(env("DEBUG"))),
            cors_config=cors_config,
            openapi_config=openapi_config,
            auth_service=env("AUTH_SERVICE"),
            files_service=env("FILES_SERVICE"),
            kafka_service=env("KAFKA_SERVICE"),
        ),
    )
