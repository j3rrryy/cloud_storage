import asyncio
import logging
from typing import Awaitable, Callable

import uvloop
from uvicorn import Config, Server

from config import setup_logging
from factories import ServiceFactory
from monitoring import MonitoringApp
from protocols import ApplicationFacadeProtocol
from settings import Settings

logger = logging.getLogger()


async def start_mail_server(application_facade: ApplicationFacadeProtocol) -> None:
    await application_facade.start_processing()


async def start_monitoring_server(is_ready: Callable[[], Awaitable[bool]]) -> None:
    app = MonitoringApp(is_ready)
    server_config = Config(
        app=app,
        loop="uvloop",
        host=Settings.MONITORING_SERVER_HOST,
        port=Settings.MONITORING_SERVER_PORT,
        limit_concurrency=Settings.MONITORING_SERVER_LIMIT_CONCURRENCY,
        limit_max_requests=Settings.MONITORING_SERVER_LIMIT_MAX_REQUESTS,
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

    is_ready = service_factory.get_is_ready()
    monitoring_task = asyncio.create_task(start_monitoring_server(is_ready))
    logger.info("Monitoring server started")

    try:
        await asyncio.gather(mail_task, monitoring_task)
    finally:
        await service_factory.close()


if __name__ == "__main__":
    uvloop.run(main())  # pragma: no cover
