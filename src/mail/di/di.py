import os

import inject
from aiokafka import AIOKafkaConsumer
from aiosmtplib import SMTP

from enums import MailTypes


def smtp_factory() -> SMTP:
    return SMTP(
        hostname=os.environ["MAIL_HOSTNAME"],
        port=int(os.environ["MAIL_PORT"]),
        username=os.environ["MAIL_USERNAME"],
        password=os.environ["MAIL_PASSWORD"],
        use_tls=True,
    )


def consumer_factory() -> AIOKafkaConsumer:
    return AIOKafkaConsumer(
        MailTypes.VERIFICATION.name,
        MailTypes.INFO.name,
        MailTypes.RESET.name,
        bootstrap_servers=os.environ["KAFKA_SERVICE"],
        group_id="mail",
    )


def configure_inject(binder: inject.Binder) -> None:
    binder.bind_to_provider(SMTP, smtp_factory)
    binder.bind_to_provider(AIOKafkaConsumer, consumer_factory)


def setup_di() -> None:
    inject.configure(configure_inject, once=True)
