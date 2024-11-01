from aiokafka import AIOKafkaConsumer

from config import load_config
from utils import MailTypes


def connect_kafka_service() -> AIOKafkaConsumer:
    config = load_config()
    return AIOKafkaConsumer(
        MailTypes.VERIFICATION.name,
        MailTypes.INFO.name,
        bootstrap_servers=config.app.kafka_service,
        group_id="mail",
    )
