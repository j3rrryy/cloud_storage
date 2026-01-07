from unittest.mock import MagicMock, PropertyMock, call

import pytest
from aiosmtplib import SMTPException

from settings import Settings


@pytest.mark.asyncio
async def test_send_mail_multiple_reconnects_with_fails(smtp_adapter, smtp):
    logger = MagicMock()
    smtp_adapter.logger = logger
    smtp.send_message.side_effect = [
        SMTPException("Server disconnected"),
        SMTPException("Server disconnected"),
        None,
    ]
    type(smtp).is_connected = PropertyMock(side_effect=[False, False, True])
    smtp.connect.side_effect = [SMTPException("Something wrong"), None]

    await smtp_adapter.send_mail(MagicMock())

    assert smtp.send_message.await_count == 3
    logger.warning.assert_has_calls(
        [
            call("Could not send mail at attempt #1: Server disconnected"),
            call("Reconnecting to SMTP server..."),
            call("Could not reconnect to SMTP server: Something wrong"),
            call("Could not send mail at attempt #2: Server disconnected"),
            call("Reconnecting to SMTP server..."),
        ]
    )
    assert smtp.connect.await_count == 2


@pytest.mark.asyncio
async def test_send_mail_not_working_all_attempts(smtp_adapter, smtp):
    logger = MagicMock()
    smtp_adapter.logger = logger
    smtp.send_message.side_effect = [
        SMTPException("Something wrong")
    ] * Settings.RETRY_COUNT
    type(smtp).is_connected = PropertyMock(return_value=True)

    with pytest.raises(RuntimeError, match="SMTP send failed"):
        await smtp_adapter.send_mail(MagicMock())

    assert smtp.send_message.await_count == Settings.RETRY_COUNT
    logger.error.assert_called_once_with(
        f"Could not send mail after {Settings.RETRY_COUNT} attempts"
    )
    assert not smtp.connect.await_count
