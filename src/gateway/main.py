import uvicorn
from litestar import Litestar
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.plugins.prometheus import PrometheusController

from config import setup_cors, setup_logging, setup_openapi, setup_prometheus
from controller import v1 as controller_v1
from factories import ServiceFactory
from settings import Settings
from utils import exception_handler


def main() -> Litestar:
    service_factory = ServiceFactory()
    return Litestar(
        path="/api",
        route_handlers=(
            PrometheusController,
            controller_v1.auth_router,
            controller_v1.file_router,
        ),
        debug=Settings.DEBUG,
        cors_config=setup_cors(),
        logging_config=setup_logging(),
        middleware=(setup_prometheus().middleware,),
        openapi_config=setup_openapi(),
        exception_handlers={HTTPException: exception_handler},
        on_startup=(service_factory.initialize,),
        on_shutdown=(service_factory.close,),
        dependencies={
            "application_facade": Provide(
                service_factory.get_application_facade,
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
        host=Settings.HOST,
        port=Settings.PORT,
        workers=Settings.WORKERS,
        limit_concurrency=Settings.LIMIT_CONCURRENCY,
        limit_max_requests=Settings.LIMIT_MAX_REQUESTS,
        reload=Settings.DEBUG,
    )
