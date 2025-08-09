import os

import uvicorn
from litestar import Litestar
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.plugins.prometheus import PrometheusController

from config import setup_cors, setup_logging, setup_openapi, setup_prometheus
from controller import v1 as controller_v1
from di import v1 as di_v1
from utils import exception_handler


def main() -> Litestar:
    return Litestar(
        path="/api",
        route_handlers=(
            PrometheusController,
            controller_v1.auth_router,
            controller_v1.file_router,
        ),
        debug=bool(int(os.environ["DEBUG"])),
        cors_config=setup_cors(),
        logging_config=setup_logging(),
        middleware=(setup_prometheus().middleware,),
        openapi_config=setup_openapi(),
        exception_handlers={HTTPException: exception_handler},
        on_startup=(di_v1.DIManager.setup,),
        on_shutdown=(di_v1.DIManager.close,),
        dependencies={
            "auth_service_v1": Provide(
                di_v1.DIManager.auth_service_factory,
                use_cache=True,
                sync_to_thread=False,
            ),
            "file_service_v1": Provide(
                di_v1.DIManager.file_service_factory,
                use_cache=True,
                sync_to_thread=False,
            ),
            "mail_service_v1": Provide(
                di_v1.DIManager.mail_service_factory,
                use_cache=True,
                sync_to_thread=False,
            ),
        },
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:main",
        factory=True,
        loop="uvloop",
        host="0.0.0.0",
        port=8000,
        limit_concurrency=1000,
        limit_max_requests=10000,
        reload=bool(int(os.environ["DEBUG"])),
    )
