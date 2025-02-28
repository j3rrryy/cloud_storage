from unittest.mock import patch

from config import load_config
from kafka import connect_kafka_service
from utils import MailTypes


@patch("kafka.connect.AIOKafkaConsumer")
def test_connect_auth_service(mock_consumer):
    connect_kafka_service()
    mock_consumer.assert_called_once_with(
        MailTypes.VERIFICATION.name,
        MailTypes.INFO.name,
        MailTypes.RESET.name,
        bootstrap_servers=load_config().app.kafka_service,
        group_id="mail",
    )
