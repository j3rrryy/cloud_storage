import asyncio
import logging

import uvloop
from prometheus_client import make_asgi_app
from uvicorn import Config, Server

from config import setup_logging
from factories import ServiceFactory
from protocols import ApplicationFacadeProtocol
from settings import Settings

logger = logging.getLogger()


async def start_mail_server(application_facade: ApplicationFacadeProtocol) -> None:
    await application_facade.start_processing()


async def start_prometheus_server() -> None:
    app = make_asgi_app()
    server_config = Config(
        app=app,
        loop="uvloop",
        host=Settings.PROMETHEUS_SERVER_HOST,
        port=Settings.PROMETHEUS_SERVER_PORT,
        limit_concurrency=Settings.PROMETHEUS_SERVER_LIMIT_CONCURRENCY,
        limit_max_requests=Settings.PROMETHEUS_SERVER_LIMIT_MAX_REQUESTS,
    )
    server = Server(server_config)
    await server.serve()


async def main() -> None:
    setup_logging()
    service_factory = ServiceFactory()
    await service_factory.initialize()

    application_facade = service_factory.get_application_facade()
    mail_task = asyncio.create_task(start_mail_server(application_facade))
    logger.info("Mail server started")

    prometheus_task = asyncio.create_task(start_prometheus_server())
    logger.info("Prometheus server started")

    try:
        await asyncio.gather(mail_task, prometheus_task)
    finally:
        await service_factory.close()


if __name__ == "__main__":
    uvloop.run(main())  # pragma: no cover
