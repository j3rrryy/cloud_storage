import asyncio
import os
from typing import Optional

import grpc
from aiokafka import AIOKafkaProducer

from proto import AuthStub, FileStub
from service.v1 import AuthService, FileService, MailService


class DIManager:
    auth_service: Optional[AuthService] = None
    file_service: Optional[FileService] = None
    mail_service: Optional[MailService] = None

    _auth_channel: Optional[grpc.aio.Channel] = None
    _file_channel: Optional[grpc.aio.Channel] = None
    _mail_producer: Optional[AIOKafkaProducer] = None
    _started = False

    @classmethod
    async def setup(cls) -> None:
        if cls._started:
            return
        try:
            await asyncio.gather(
                cls.setup_auth_service(),
                cls.setup_file_service(),
                cls.setup_mail_service(),
            )
            cls._started = True
        except Exception:
            await cls.close()
            raise

    @classmethod
    async def close(cls) -> None:
        if cls._auth_channel is not None:
            try:
                await cls._auth_channel.close()
            finally:
                cls._auth_channel = None
                cls.auth_service = None

        if cls._file_channel is not None:
            try:
                await cls._file_channel.close()
            finally:
                cls._file_channel = None
                cls.file_service = None

        if cls._mail_producer is not None:
            try:
                await cls._mail_producer.stop()
            finally:
                cls._mail_producer = None
                cls.mail_service = None

        cls._started = False

    @classmethod
    async def setup_auth_service(cls) -> None:
        cls._auth_channel = grpc.aio.insecure_channel(
            os.environ["AUTH_SERVICE"],
            options=[
                ("grpc.keepalive_time_ms", 60000),
                ("grpc.keepalive_timeout_ms", 10000),
                ("grpc.keepalive_permit_without_calls", 1),
            ],
            compression=grpc.Compression.Deflate,
        )
        await asyncio.wait_for(cls._auth_channel.channel_ready(), timeout=5)
        stub = AuthStub(cls._auth_channel)
        cls.auth_service = AuthService(stub)

    @classmethod
    async def setup_file_service(cls) -> None:
        cls._file_channel = grpc.aio.insecure_channel(
            os.environ["FILE_SERVICE"],
            options=[
                ("grpc.keepalive_time_ms", 60000),
                ("grpc.keepalive_timeout_ms", 10000),
                ("grpc.keepalive_permit_without_calls", 1),
            ],
            compression=grpc.Compression.Deflate,
        )
        await asyncio.wait_for(cls._file_channel.channel_ready(), timeout=5)
        stub = FileStub(cls._file_channel)
        cls.file_service = FileService(stub)

    @classmethod
    async def setup_mail_service(cls) -> None:
        cls._mail_producer = AIOKafkaProducer(
            bootstrap_servers=os.environ["KAFKA_SERVICE"],
            compression_type="lz4",
            acks=1,
            linger_ms=10,
            request_timeout_ms=10000,
        )
        await cls._mail_producer.start()
        cls.mail_service = MailService(cls._mail_producer)

    @classmethod
    def auth_service_factory(cls) -> AuthService:
        if not cls.auth_service:
            raise RuntimeError(
                "AuthService not initialized; DIManager.setup() was not called"
            )
        return cls.auth_service

    @classmethod
    def file_service_factory(cls) -> FileService:
        if not cls.file_service:
            raise RuntimeError(
                "FileService not initialized; DIManager.setup() was not called"
            )
        return cls.file_service

    @classmethod
    def mail_service_factory(cls) -> MailService:
        if not cls.mail_service:
            raise RuntimeError(
                "MailService not initialized; DIManager.setup() was not called"
            )
        return cls.mail_service
