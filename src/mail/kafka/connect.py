from aiokafka import AIOKafkaConsumer

from config import load_config
from utils import MailTypes


def connect_kafka_service() -> AIOKafkaConsumer:
    return AIOKafkaConsumer(
        MailTypes.VERIFICATION.name,
        MailTypes.INFO.name,
        MailTypes.RESET.name,
        bootstrap_servers=load_config().app.kafka_service,
        group_id="mail",
    )
