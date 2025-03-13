import uvicorn
from litestar import Litestar
from litestar.di import Provide
from litestar.plugins.prometheus import PrometheusController

from config import load_config
from controller.v1.auth import auth_router as auth_v1
from controller.v1.file import file_router as file_v1
from service import connect_auth_service, connect_file_service, connect_mail_service

config = load_config()

app = Litestar(
    path="/api",
    route_handlers=(PrometheusController, auth_v1, file_v1),
    debug=config.app.debug,
    logging_config=config.app.litestar_logging_config,
    cors_config=config.app.cors_config,
    openapi_config=config.app.openapi_config,
    middleware=(config.app.prometheus_config.middleware,),
    request_max_body_size=None,
    dependencies={
        "auth_service": Provide(connect_auth_service),
        "file_service": Provide(connect_file_service),
        "mail_service": Provide(connect_mail_service),
    },
)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        loop="uvloop",
        host="0.0.0.0",
        port=8000,
        workers=10,
        limit_concurrency=1000,
        limit_max_requests=10000,
        reload=config.app.debug,
    )
