import pickle
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from controller import MailController
from enums import MailTypes
from service import MailService

from .mocks import BROWSER, CODE, EMAIL, USER_IP, USERNAME, VERIFICATION_TOKEN


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mail_data",
    [
        (
            MailTypes.VERIFICATION.name,
            {
                "verification_token": VERIFICATION_TOKEN,
                "email": EMAIL,
                "username": USERNAME,
            },
        ),
        (
            MailTypes.INFO.name,
            {
                "user_ip": USER_IP,
                "browser": BROWSER,
                "email": EMAIL,
                "username": USERNAME,
            },
        ),
        (MailTypes.RESET.name, {"code": CODE, "email": EMAIL, "username": USERNAME}),
    ],
)
@patch.object(MailController, "_email_sent_counter")
@patch("controller.mail_controller.DTOFactory.from_message")
async def test_process_messages(mock_dto_factory, mock_sent_counter, mail_data):
    topic, data = mail_data
    mock_msg = MagicMock()
    mock_msg.topic = topic
    mock_msg.value = pickle.dumps(data)

    async def mock_aiter(_):
        yield mock_msg

    mock_consumer = MagicMock()
    mock_consumer.__aenter__ = AsyncMock()
    mock_consumer.__aexit__ = AsyncMock()
    mock_consumer.__aiter__ = mock_aiter

    mock_dto = MagicMock()
    mock_dto.email = EMAIL
    mock_dto_factory.return_value = mock_dto

    with (
        patch.object(MailController, "_logger", new_callable=MagicMock) as mock_logger,
        patch.object(
            MailService, "send_email", new_callable=AsyncMock
        ) as mock_send_email,
    ):
        await MailController.process_messages(mock_consumer)

        mock_dto_factory.assert_called_once_with(mock_msg)
        mock_send_email.assert_awaited_once()
        mock_logger.info.assert_called_once_with(f"Sent {topic} mail to {EMAIL}")
        mock_sent_counter.labels.assert_called_once_with(topic)
        mock_sent_counter.labels.return_value.inc.assert_called_once()


@pytest.mark.asyncio
@patch.object(MailController, "_email_failed_counter")
@patch("controller.mail_controller.DTOFactory.from_message")
async def test_process_messages_exception(mock_dto_factory, mock_failed_counter):
    topic = MailTypes.VERIFICATION.name
    mock_msg = MagicMock()
    mock_msg.topic = topic
    mock_msg.value = pickle.dumps(
        {"verification_token": VERIFICATION_TOKEN, "email": EMAIL, "username": USERNAME}
    )

    async def mock_aiter(_):
        yield mock_msg

    mock_consumer = MagicMock()
    mock_consumer.__aenter__ = AsyncMock()
    mock_consumer.__aexit__ = AsyncMock()
    mock_consumer.__aiter__ = mock_aiter

    test_exception = Exception("Test exception")
    mock_dto_factory.side_effect = test_exception

    with patch.object(MailController, "_logger", new_callable=MagicMock) as mock_logger:
        await MailController.process_messages(mock_consumer)

        mock_dto_factory.assert_called_once_with(mock_msg)
        mock_logger.exception.assert_called_once_with(test_exception)
        mock_failed_counter.labels.assert_called_once_with(topic)
        mock_failed_counter.labels.return_value.inc.assert_called_once()
