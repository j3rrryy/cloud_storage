from dataclasses import dataclass

from environs import Env
from litestar.config.cors import CORSConfig
from litestar.logging import LoggingConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar.plugins.prometheus import PrometheusConfig
from uvicorn.config import LOGGING_CONFIG

__all__ = ["Config", "load_config"]


@dataclass(slots=True)
class AppConfig:
    debug: bool
    litestar_logging_config: LoggingConfig
    cors_config: CORSConfig
    openapi_config: OpenAPIConfig
    prometheus_config: PrometheusConfig
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


def load_config():
    env = Env()
    env.read_env()

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
    litestar_logging_config = LoggingConfig(
        formatters={
            "standard": {
                "format": "%(asctime)s | %(levelname)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        }
    )
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
    prometheus_config = PrometheusConfig(
        app_name=env("APP_NAME"),
        prefix="gateway",
        excluded_http_methods=("PUT"),
        group_path=True,
    )

    return Config(
        AppConfig(
            bool(int(env("DEBUG"))),
            litestar_logging_config,
            cors_config,
            openapi_config,
            prometheus_config,
            env("AUTH_SERVICE"),
            env("FILES_SERVICE"),
            env("KAFKA_SERVICE"),
        )
    )
