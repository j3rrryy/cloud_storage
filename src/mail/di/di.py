import asyncio
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import inject
from aiokafka import AIOKafkaConsumer
from aiosmtplib import SMTP

from enums import MailTypes


class SMTPManager:
    _pool_size = 5
    _smtp_pool: Optional[asyncio.Queue[SMTP]] = None
    _started = False

    @classmethod
    async def setup(cls) -> None:
        if cls._started:
            return
        try:
            cls._smtp_pool = asyncio.Queue(cls._pool_size)

            for _ in range(cls._pool_size):
                smtp = await cls._create_smtp_connection()
                cls._smtp_pool.put_nowait(smtp)

            cls._started = True
        except Exception:
            await cls.close()
            raise

    @classmethod
    async def close(cls) -> None:
        if cls._smtp_pool is not None:
            for _ in range(cls._pool_size):
                try:
                    smtp = await asyncio.wait_for(cls._smtp_pool.get(), 1.5)
                    await smtp.quit()
                except Exception:
                    pass

            cls._smtp_pool = None
        cls._started = False

    @classmethod
    @asynccontextmanager
    async def smtp_factory(cls) -> AsyncGenerator[SMTP, None]:
        if not cls._smtp_pool or not cls._started:
            raise RuntimeError(
                "SMTP not initialized; SMTPManager.setup() was not called"
            )

        smtp = await cls._smtp_pool.get()

        try:
            if not smtp.is_connected:
                await smtp.quit()
                smtp = await cls._create_smtp_connection()
            yield smtp
        except Exception:
            try:
                await smtp.quit()
            except Exception:
                pass
            smtp = await cls._create_smtp_connection()
        finally:
            cls._smtp_pool.put_nowait(smtp)

    @staticmethod
    async def _create_smtp_connection() -> SMTP:
        smtp = SMTP(
            hostname=os.environ["MAIL_HOSTNAME"],
            port=int(os.environ["MAIL_PORT"]),
            username=os.environ["MAIL_USERNAME"],
            password=os.environ["MAIL_PASSWORD"],
            use_tls=True,
            timeout=10,
        )
        await smtp.connect()
        return smtp


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
                bootstrap_servers=os.environ["KAFKA_SERVICE"],
                group_id="mail",
                auto_offset_reset="earliest",
                max_poll_records=1000,
                request_timeout_ms=10000,
            )
            await cls.consumer.start()
            cls._started = True
        except:
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
