import asyncio

import grpc
import picologging as logging
import uvloop
from grpc_accesslog import AsyncAccessLogInterceptor, handlers
from prometheus_client import make_asgi_app
from py_async_grpc_prometheus.prometheus_async_server_interceptor import (
    PromAsyncServerInterceptor,
)
from uvicorn import Config, Server

from config import setup_cache, setup_logging
from controller import FileController
from di import setup_di
from proto import add_FileServicer_to_server

logger = logging.getLogger()


async def start_grpc_server() -> None:
    server = grpc.aio.server(
        interceptors=(
            AsyncAccessLogInterceptor(logger=logger, handlers=[handlers.request]),  # type: ignore
            PromAsyncServerInterceptor(enable_handling_time_histogram=True),
        ),
        options=[
            ("grpc.keepalive_time_ms", 60000),
            ("grpc.keepalive_timeout_ms", 10000),
            ("grpc.keepalive_permit_without_calls", 1),
        ],
        maximum_concurrent_rpcs=1000,
        compression=grpc.Compression.Deflate,
    )
    add_FileServicer_to_server(FileController(), server)
    server.add_insecure_port("[::]:50051")

    await server.start()
    logger.info("gRPC server started")
    await server.wait_for_termination()


async def start_prometheus_server() -> None:
    app = make_asgi_app()
    server_config = Config(
        app=app,
        loop="uvloop",
        host="0.0.0.0",
        port=8000,
        limit_concurrency=50,
        limit_max_requests=10000,
    )
    server = Server(server_config)
    await server.serve()


async def main() -> None:
    setup_di()
    setup_logging()
    setup_cache()

    grpc_task = asyncio.create_task(start_grpc_server())
    prometheus_task = asyncio.create_task(start_prometheus_server())
    await asyncio.gather(grpc_task, prometheus_task)


if __name__ == "__main__":
    uvloop.run(main())  # pragma: no cover
