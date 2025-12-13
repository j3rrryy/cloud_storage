import asyncio

import picologging as logging
import uvloop
from prometheus_client import make_asgi_app
from uvicorn import Config, Server

from config import setup_logging
from controller import MailController
from di import ConsumerManager, SMTPManager, setup_di
from settings import Settings

logger = logging.getLogger()


async def start_mail_server() -> None:
    await MailController.process_messages()  # type: ignore


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
    await setup_di()
    setup_logging()

    mail_task = asyncio.create_task(start_mail_server())
    logger.info("Mail server started")
    prometheus_task = asyncio.create_task(start_prometheus_server())
    logger.info("Prometheus server started")

    try:
        await asyncio.gather(mail_task, prometheus_task)
    finally:
        await ConsumerManager.close()
        await SMTPManager.close()


if __name__ == "__main__":
    uvloop.run(main())  # pragma: no cover
