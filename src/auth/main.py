import asyncio

import grpc
import picologging as logging
import uvloop
from prometheus_client import make_asgi_app
from py_async_grpc_prometheus.prometheus_async_server_interceptor import (
    PromAsyncServerInterceptor,
)
from uvicorn import Config, Server

from config import setup_cache, setup_logging
from controller import AuthController
from di import SessionManager, setup_di
from proto import add_AuthServicer_to_server
from settings import Settings

logger = logging.getLogger()


async def start_grpc_server() -> None:
    server = grpc.aio.server(
        interceptors=(PromAsyncServerInterceptor(),),
        options=[
            ("grpc.keepalive_time_ms", 60000),
            ("grpc.keepalive_timeout_ms", 10000),
            ("grpc.keepalive_permit_without_calls", 1),
        ],
        maximum_concurrent_rpcs=Settings.GRPC_SERVER_MAXIMUM_CONCURRENT_RPCS,
        compression=grpc.Compression.Deflate,
    )
    add_AuthServicer_to_server(AuthController(), server)
    server.add_insecure_port(Settings.GRPC_SERVER_ADDRESS)

    await server.start()
    await server.wait_for_termination()


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
    setup_cache()

    grpc_task = asyncio.create_task(start_grpc_server())
    logger.info("gRPC server started")
    prometheus_task = asyncio.create_task(start_prometheus_server())
    logger.info("Prometheus server started")

    try:
        await asyncio.gather(grpc_task, prometheus_task)
    finally:
        await SessionManager.close()


if __name__ == "__main__":
    uvloop.run(main())  # pragma: no cover
