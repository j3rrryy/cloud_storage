import os

import uvicorn
from litestar import Litestar
from litestar.di import Provide
from litestar.plugins.prometheus import PrometheusController

from config import setup_cors, setup_logging, setup_openapi, setup_prometheus
from controller.v1 import auth_router_v1, file_router_v1
from di.v1 import auth_service_factory, file_service_factory, mail_service_factory


def main() -> Litestar:
    return Litestar(
        path="/api",
        route_handlers=(PrometheusController, auth_router_v1, file_router_v1),
        debug=bool(int(os.environ["DEBUG"])),
        cors_config=setup_cors(),
        logging_config=setup_logging(),
        middleware=(setup_prometheus().middleware,),
        openapi_config=setup_openapi(),
        request_max_body_size=None,
        dependencies={
            "auth_service": Provide(auth_service_factory),
            "file_service": Provide(file_service_factory),
            "mail_service": Provide(mail_service_factory),
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
