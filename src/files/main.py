from concurrent import futures

import grpc
import uvloop
from grpc_accesslog import AsyncAccessLogInterceptor, handlers

from config import load_config
from proto import add_FilesServicer_to_server
from service import FilesServicer


async def main():
    config = load_config()
    logger = config.app.logger

    server = grpc.aio.server(
        migration_thread_pool=futures.ThreadPoolExecutor(max_workers=10),
        interceptors=(
            AsyncAccessLogInterceptor(logger=logger, handlers=[handlers.request]),
        ),
        compression=grpc.Compression.Deflate,
        options=(("grpc.max_receive_message_length", 6 * 1024 * 1024),),
    )
    add_FilesServicer_to_server(FilesServicer(), server)
    server.add_insecure_port("[::]:50051")

    await server.start()
    logger.info("Server started")
    await server.wait_for_termination()


if __name__ == "__main__":
    uvloop.run(main())
