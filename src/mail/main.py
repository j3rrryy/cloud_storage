import asyncio

import uvloop
from prometheus_client import make_asgi_app
from uvicorn import Config, Server

from config import load_config
from controller import MailController
from kafka import connect_kafka_service


async def start_mail_server():
    config = load_config()

    consumer = connect_kafka_service()
    controller = MailController(consumer)

    config.app.logger.info("Server started")
    await controller.process_messages()


async def start_prometheus_server():
    app = make_asgi_app()
    server_config = Config(app=app, loop="uvloop", host="0.0.0.0", port=8000)
    server = Server(server_config)
    await server.serve()


async def main():
    mail_task = asyncio.create_task(start_mail_server())
    prometheus_task = asyncio.create_task(start_prometheus_server())
    await asyncio.gather(mail_task, prometheus_task)


if __name__ == "__main__":
    uvloop.run(main())  # pragma: no cover
