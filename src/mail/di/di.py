from typing import Optional

import inject
from aiokafka import AIOKafkaConsumer
from aiosmtplib import SMTP

from enums import MailTypes
from settings import Settings


class SMTPManager:
    smtp: Optional[SMTP] = None
    _started = False

    @classmethod
    async def setup(cls) -> None:
        if cls._started:
            return
        try:
            cls.smtp = SMTP(
                username=Settings.MAIL_USERNAME,
                password=Settings.MAIL_PASSWORD,
                hostname=Settings.MAIL_HOSTNAME,
                port=Settings.MAIL_PORT,
                use_tls=Settings.MAIL_TLS,
            )
            await cls.smtp.connect()
            cls._started = True
        except Exception:
            await cls.close()
            raise

    @classmethod
    async def close(cls) -> None:
        if cls.smtp is not None:
            try:
                await cls.smtp.quit()
            finally:
                cls.smtp = None
        cls._started = False

    @classmethod
    def smtp_factory(cls) -> SMTP:
        if not cls.smtp or not cls._started:
            raise RuntimeError(
                "SMTP not initialized; SMTPManager.setup() was not called"
            )
        return cls.smtp


class ConsumerManager:
    consumer: Optional[AIOKafkaConsumer] = None
    _started = False

    @classmethod
    async def setup(cls) -> None:
        if cls._started:
            return
        try:
            cls.consumer = AIOKafkaConsumer(
                MailTypes.VERIFICATION.name,
                MailTypes.INFO.name,
                MailTypes.RESET.name,
                bootstrap_servers=Settings.KAFKA_SERVICE,
                group_id=Settings.KAFKA_GROUP_ID,
                auto_offset_reset="earliest",
            )
            await cls.consumer.start()
            cls._started = True
        except Exception:
            await cls.close()
            raise

    @classmethod
    async def close(cls) -> None:
        if cls.consumer is not None:
            try:
                await cls.consumer.stop()
            finally:
                cls.consumer = None
        cls._started = False

    @classmethod
    def consumer_factory(cls) -> AIOKafkaConsumer:
        if not cls.consumer or not cls._started:
            raise RuntimeError(
                "AIOKafkaConsumer not initialized; ConsumerManager.setup() was not called"
            )
        return cls.consumer


def configure_inject(binder: inject.Binder) -> None:
    binder.bind_to_provider(SMTP, SMTPManager.smtp_factory)
    binder.bind_to_provider(AIOKafkaConsumer, ConsumerManager.consumer_factory)


async def setup_di() -> None:
    await SMTPManager.setup()
    await ConsumerManager.setup()
    inject.configure(configure_inject, once=True)
