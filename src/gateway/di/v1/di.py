import os
from typing import Any, AsyncGenerator

import grpc
from aiokafka import AIOKafkaProducer

from proto import AuthStub, FileStub
from service.v1 import AuthService, FileService, MailService


async def auth_service_factory() -> AsyncGenerator[AuthService, Any]:
    async with grpc.aio.insecure_channel(
        os.environ["AUTH_SERVICE"], compression=grpc.Compression.Deflate
    ) as channel:
        stub = AuthStub(channel)
        yield AuthService(stub)


async def file_service_factory() -> AsyncGenerator[FileService, Any]:
    async with grpc.aio.insecure_channel(
        os.environ["FILE_SERVICE"], compression=grpc.Compression.Deflate
    ) as channel:
        stub = FileStub(channel)
        yield FileService(stub)


async def mail_service_factory() -> AsyncGenerator[MailService, Any]:
    async with AIOKafkaProducer(
        bootstrap_servers=os.environ["KAFKA_SERVICE"],
        compression_type="lz4",
        acks=1,
        linger_ms=10,
    ) as producer:
        yield MailService(producer)
