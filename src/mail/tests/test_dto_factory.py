import msgspec
import pytest
from aiokafka import ConsumerRecord

from dto import InfoMailDTO, ResetMailDTO, VerificationMailDTO
from dto.factory import DTOFactory
from enums import MailTypes

from .mocks import BROWSER, CODE, EMAIL, USER_IP, USERNAME, VERIFICATION_TOKEN


@pytest.mark.parametrize(
    "topic, data, expected_cls",
    [
        (
            MailTypes.VERIFICATION.name,
            {
                "verification_token": VERIFICATION_TOKEN,
                "email": EMAIL,
                "username": USERNAME,
            },
            VerificationMailDTO,
        ),
        (
            MailTypes.INFO.name,
            {
                "user_ip": USER_IP,
                "browser": BROWSER,
                "email": EMAIL,
                "username": USERNAME,
            },
            InfoMailDTO,
        ),
        (
            MailTypes.RESET.name,
            {"code": CODE, "email": EMAIL, "username": USERNAME},
            ResetMailDTO,
        ),
    ],
)
def test_from_message(topic, data, expected_cls):
    record = ConsumerRecord(
        topic=topic,
        partition=0,
        offset=0,
        timestamp=0,
        timestamp_type=0,
        key=None,
        value=msgspec.msgpack.encode(data),
        headers=[],
        checksum=None,
        serialized_key_size=0,
        serialized_value_size=0,
    )

    res = DTOFactory.from_message(record)

    assert isinstance(res, expected_cls)
    for key, value in data.items():
        assert getattr(res, key) == value


def test_from_message_empty_value():
    record = ConsumerRecord(
        topic=MailTypes.VERIFICATION.name,
        partition=0,
        offset=0,
        timestamp=0,
        timestamp_type=0,
        key=None,
        value=None,
        headers=[],
        checksum=None,
        serialized_key_size=0,
        serialized_value_size=0,
    )

    with pytest.raises(ValueError, match="The message is empty"):
        DTOFactory.from_message(record)
