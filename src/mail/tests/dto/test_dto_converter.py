import pytest

from dto import (
    EmailConfirmationMailDTO,
    MessageToDTOConverter,
    NewLoginMailDTO,
    PasswordResetMailDTO,
)
from enums import MailTypes

from ..mocks import BROWSER, CODE, EMAIL, TOKEN, USER_IP, USERNAME


@pytest.mark.parametrize(
    "topic, message, expected_dto_cls",
    [
        (
            MailTypes.EMAIL_CONFIRMATION.name,
            {
                "username": USERNAME,
                "email": EMAIL,
                "token": TOKEN,
            },
            EmailConfirmationMailDTO,
        ),
        (
            MailTypes.NEW_LOGIN.name,
            {
                "username": USERNAME,
                "email": EMAIL,
                "user_ip": USER_IP,
                "browser": BROWSER,
            },
            NewLoginMailDTO,
        ),
        (
            MailTypes.PASSWORD_RESET.name,
            {"username": USERNAME, "email": EMAIL, "code": CODE},
            PasswordResetMailDTO,
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
        "token": TOKEN,
        "email": EMAIL,
        "username": USERNAME,
    }

    with pytest.raises(ValueError, match=f"Unsupported mail type: {topic}"):
        MessageToDTOConverter.convert(topic, message)


def test_convert_invalid_data():
    topic = MailTypes.EMAIL_CONFIRMATION.name
    message = {"invalid_key": "invalid_value"}

    with pytest.raises(ValueError, match=f"Invalid message data for {topic}: "):
        MessageToDTOConverter.convert(topic, message)
