import pytest

from dto import LoginMailDTO, MessageToDTOConverter, ResetMailDTO, VerificationMailDTO
from enums import MailTypes

from ..mocks import BROWSER, CODE, EMAIL, USER_IP, USERNAME, VERIFICATION_TOKEN


@pytest.mark.parametrize(
    "topic, message, expected_dto_cls",
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
            MailTypes.LOGIN.name,
            {
                "user_ip": USER_IP,
                "browser": BROWSER,
                "email": EMAIL,
                "username": USERNAME,
            },
            LoginMailDTO,
        ),
        (
            MailTypes.RESET.name,
            {"code": CODE, "email": EMAIL, "username": USERNAME},
            ResetMailDTO,
        ),
    ],
)
def test_convert(topic, message, expected_dto_cls):
    dto = MessageToDTOConverter.convert(topic, message)

    assert isinstance(dto, expected_dto_cls)
    for key, value in message.items():
        assert getattr(dto, key) == value


def test_convert_unsupported_topic():
    topic = "unsupported_topic"
    message = {
        "verification_token": VERIFICATION_TOKEN,
        "email": EMAIL,
        "username": USERNAME,
    }

    with pytest.raises(ValueError, match=f"Unsupported mail type: {topic}"):
        MessageToDTOConverter.convert(topic, message)


def test_convert_invalid_data():
    topic = MailTypes.VERIFICATION.name
    message = {"invalid_key": "invalid_value"}

    with pytest.raises(ValueError, match=f"Invalid message data for {topic}: "):
        MessageToDTOConverter.convert(topic, message)
