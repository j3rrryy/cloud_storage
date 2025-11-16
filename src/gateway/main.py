import uvicorn
from litestar import Litestar
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.plugins.prometheus import PrometheusController

from config import setup_cors, setup_logging, setup_openapi, setup_prometheus
from controller import v1 as controller_v1
from factories import ServiceFactory
from settings import AppSettings
from utils import exception_handler

service_factory = ServiceFactory()


async def startup_handler() -> None:
    await service_factory.initialize()


async def shutdown_handler() -> None:
    await service_factory.close()


def get_application_facade():
    return service_factory.get_application_facade()


def main() -> Litestar:
    return Litestar(
        path="/api",
        route_handlers=(
            PrometheusController,
            controller_v1.auth_router,
            controller_v1.file_router,
        ),
        debug=AppSettings.DEBUG,
        cors_config=setup_cors(),
        logging_config=setup_logging(),
        middleware=(setup_prometheus().middleware,),
        openapi_config=setup_openapi(),
        exception_handlers={HTTPException: exception_handler},
        on_startup=(startup_handler,),
        on_shutdown=(shutdown_handler,),
        dependencies={
            "application_facade": Provide(get_application_facade, use_cache=True),
        },
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:main",
        factory=True,
        loop="uvloop",
        host=AppSettings.HOST,
        port=AppSettings.PORT,
        workers=AppSettings.WORKERS,
        limit_concurrency=AppSettings.LIMIT_CONCURRENCY,
        limit_max_requests=AppSettings.LIMIT_MAX_REQUESTS,
        reload=AppSettings.DEBUG,
    )
