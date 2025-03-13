from typing import Any, AsyncGenerator

import grpc
from aiokafka import AIOKafkaProducer

from config import load_config
from proto import AuthStub, FileStub

from .auth import AuthService
from .file import FileService
from .mail import MailService

config = load_config()


async def connect_auth_service() -> AsyncGenerator[AuthService, Any]:
    async with grpc.aio.insecure_channel(
        config.app.auth_service, compression=grpc.Compression.Deflate
    ) as channel:
        stub = AuthStub(channel)
        yield AuthService(stub)


async def connect_file_service() -> AsyncGenerator[FileService, Any]:
    async with grpc.aio.insecure_channel(
        config.app.file_service, compression=grpc.Compression.Deflate
    ) as channel:
        stub = FileStub(channel)
        yield FileService(stub)


async def connect_mail_service() -> AsyncGenerator[MailService, Any]:
    async with AIOKafkaProducer(
        bootstrap_servers=config.app.kafka_service, compression_type="lz4"
    ) as producer:
        yield MailService(producer)
