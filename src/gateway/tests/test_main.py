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
    assert on_startup == (main.startup_handler,)
    on_shutdown = kwargs["on_shutdown"]
    assert on_shutdown == (main.shutdown_handler,)
    deps = kwargs["dependencies"]
    assert deps["application_facade"].use_cache
    assert not deps["application_facade"].sync_to_thread
    assert deps["application_facade"].dependency == main.get_application_facade


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
