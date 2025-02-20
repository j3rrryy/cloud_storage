from typing import Any, AsyncGenerator

import grpc
from aiokafka import AIOKafkaProducer

from config import load_config
from proto import AuthStub, FilesStub

from .auth import Auth
from .files import Files
from .mail import Mail

config = load_config()


async def connect_auth_service() -> AsyncGenerator[Auth, Any]:
    async with grpc.aio.insecure_channel(
        config.app.auth_service, compression=grpc.Compression.Deflate
    ) as channel:
        stub = AuthStub(channel)
        yield Auth(stub)


async def connect_files_service() -> AsyncGenerator[Files, Any]:
    async with grpc.aio.insecure_channel(
        config.app.files_service,
        compression=grpc.Compression.Deflate,
    ) as channel:
        stub = FilesStub(channel)
        yield Files(stub)


async def connect_mail_service() -> AsyncGenerator[Mail, Any]:
    async with AIOKafkaProducer(
        bootstrap_servers=config.app.kafka_service,
        compression_type="lz4",
    ) as producer:
        yield Mail(producer)
