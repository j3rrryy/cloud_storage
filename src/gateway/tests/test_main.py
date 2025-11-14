import importlib
import os
from unittest.mock import patch

from litestar.config.cors import CORSConfig
from litestar.exceptions import HTTPException
from litestar.logging import LoggingConfig
from litestar.middleware.base import DefineMiddleware
from litestar.openapi.config import OpenAPIConfig
from litestar.plugins.prometheus import PrometheusController

import main
from controller import v1 as controller_v1
from di import v1 as di_v1
from utils import exception_handler


@patch("litestar.Litestar")
def test_app(mock_litestar):
    importlib.reload(main)

    main.main()

    _, kwargs = mock_litestar.call_args
    assert kwargs["path"] == "/api"
    assert kwargs["route_handlers"] == (
        PrometheusController,
        controller_v1.auth_router,
        controller_v1.file_router,
    )
    assert kwargs["debug"] == bool(int(os.environ["DEBUG"]))
    assert isinstance(kwargs["cors_config"], CORSConfig)
    assert isinstance(kwargs["logging_config"], LoggingConfig)
    assert isinstance(kwargs["openapi_config"], OpenAPIConfig)
    middleware = kwargs["middleware"]
    assert len(middleware) == 1
    assert isinstance(middleware[0], DefineMiddleware)
    exc_handlers = kwargs["exception_handlers"]
    assert len(middleware) == 1
    assert isinstance(exc_handlers[HTTPException], type(exception_handler))
    on_startup = kwargs["on_startup"]
    assert on_startup == (di_v1.DIManager.setup,)
    on_shutdown = kwargs["on_shutdown"]
    assert on_shutdown == (di_v1.DIManager.close,)
    deps = kwargs["dependencies"]
    assert deps["auth_service_v1"].use_cache
    assert deps["file_service_v1"].use_cache
    assert deps["mail_service_v1"].use_cache
    assert not deps["auth_service_v1"].sync_to_thread
    assert not deps["file_service_v1"].sync_to_thread
    assert not deps["mail_service_v1"].sync_to_thread
    assert deps["auth_service_v1"].dependency == di_v1.DIManager.auth_service_factory
    assert deps["file_service_v1"].dependency == di_v1.DIManager.file_service_factory
    assert deps["mail_service_v1"].dependency == di_v1.DIManager.mail_service_factory


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
            workers=2,
            limit_concurrency=500,
            limit_max_requests=50000,
            reload=bool(int(os.environ["DEBUG"])),
        )
