import importlib
import os
from unittest.mock import patch

from litestar.config.cors import CORSConfig
from litestar.di import Provide
from litestar.logging import LoggingConfig
from litestar.middleware.base import DefineMiddleware
from litestar.openapi.config import OpenAPIConfig
from litestar.plugins.prometheus import PrometheusController

import main
from controller.v1 import auth_router_v1, file_router_v1
from di.v1 import auth_service_factory, file_service_factory, mail_service_factory


@patch("litestar.Litestar")
def test_app(mock_litestar):
    importlib.reload(main)
    main.main()

    _, kwargs = mock_litestar.call_args

    assert kwargs["path"] == "/api"
    assert kwargs["route_handlers"] == (
        PrometheusController,
        auth_router_v1,
        file_router_v1,
    )
    assert kwargs["debug"] == bool(int(os.environ["DEBUG"]))
    assert isinstance(kwargs["cors_config"], CORSConfig)
    assert isinstance(kwargs["logging_config"], LoggingConfig)
    assert isinstance(kwargs["openapi_config"], OpenAPIConfig)
    assert kwargs["request_max_body_size"] is None

    middleware = kwargs["middleware"]
    assert isinstance(middleware, tuple)
    assert len(middleware) == 1
    assert isinstance(middleware[0], DefineMiddleware)

    deps = kwargs["dependencies"]
    assert isinstance(deps["auth_service"], Provide)
    assert deps["auth_service"].dependency == auth_service_factory
    assert deps["file_service"].dependency == file_service_factory
    assert deps["mail_service"].dependency == mail_service_factory


@patch("uvicorn.run")
def test_uvicorn(mock_run):
    with open("main.py") as file:
        code = compile(file.read(), str("main.py"), "exec")
        exec(code, {"__name__": "__main__"})

        mock_run.assert_called_once_with(
            "main:main",
            factory=True,
            loop="uvloop",
            host="0.0.0.0",
            port=8000,
            limit_concurrency=1000,
            limit_max_requests=10000,
            reload=bool(int(os.environ["DEBUG"])),
        )
