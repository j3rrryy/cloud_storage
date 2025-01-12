import asyncio
from concurrent import futures

import grpc
import uvloop
from grpc_accesslog import AsyncAccessLogInterceptor, handlers
from py_async_grpc_prometheus.prometheus_async_server_interceptor import (
    PromAsyncServerInterceptor,
)
from prometheus_client import make_asgi_app
from uvicorn import Config, Server

from config import load_config
from proto import add_AuthServicer_to_server
from service import AuthServicer


async def start_grpc_server():
    config = load_config()
    logger = config.app.logger

    server = grpc.aio.server(
        migration_thread_pool=futures.ThreadPoolExecutor(max_workers=10),
        interceptors=(
            AsyncAccessLogInterceptor(logger=logger, handlers=[handlers.request]),
            PromAsyncServerInterceptor(enable_handling_time_histogram=True),
        ),
        compression=grpc.Compression.Deflate,
    )
    add_AuthServicer_to_server(AuthServicer(), server)
    server.add_insecure_port("[::]:50051")

    await server.start()
    logger.info("gRPC server started")
    await server.wait_for_termination()


async def start_prometheus_server():
    app = make_asgi_app()
    server_config = Config(app=app, loop="uvloop", host="0.0.0.0", port=8000)
    server = Server(config=server_config)
    await server.serve()


async def main():
    grpc_task = asyncio.create_task(start_grpc_server())
    prometheus_task = asyncio.create_task(start_prometheus_server())
    await asyncio.gather(grpc_task, prometheus_task)


if __name__ == "__main__":
    uvloop.run(main())
