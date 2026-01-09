import asyncio
import logging
from typing import Awaitable, Callable

import grpc
import uvloop
from py_async_grpc_prometheus.prometheus_async_server_interceptor import (
    PromAsyncServerInterceptor,
)
from uvicorn import Config, Server

from config import setup_logging
from factories import ServiceFactory
from monitoring import MonitoringApp
from proto import FileServicer, add_FileServicer_to_server
from settings import Settings
from utils import ExceptionInterceptor

logger = logging.getLogger()


async def start_grpc_server(file_controller: FileServicer) -> None:
    server = grpc.aio.server(
        interceptors=(PromAsyncServerInterceptor(), ExceptionInterceptor()),
        options=[
            ("grpc.keepalive_time_ms", 60000),
            ("grpc.keepalive_timeout_ms", 10000),
            ("grpc.keepalive_permit_without_calls", 1),
        ],
        maximum_concurrent_rpcs=Settings.GRPC_SERVER_MAXIMUM_CONCURRENT_RPCS,
        compression=grpc.Compression.Deflate,
    )
    add_FileServicer_to_server(file_controller, server)
    server.add_insecure_port(Settings.GRPC_SERVER_ADDRESS)

    await server.start()
    await server.wait_for_termination()


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

    file_controller = service_factory.get_file_controller()
    grpc_task = asyncio.create_task(start_grpc_server(file_controller))
    logger.info("gRPC server started")

    is_ready = service_factory.get_is_ready()
    monitoring_task = asyncio.create_task(start_monitoring_server(is_ready))
    logger.info("Monitoring server started")

    try:
        await asyncio.gather(grpc_task, monitoring_task)
    finally:
        await service_factory.close()


if __name__ == "__main__":
    uvloop.run(main())  # pragma: no cover
