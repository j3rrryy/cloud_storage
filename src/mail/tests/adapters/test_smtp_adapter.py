from unittest.mock import MagicMock

import pytest
from aiosmtplib import SMTPServerDisconnected

from settings import Settings


@pytest.mark.asyncio
async def test_send_mail_server_disconnected_reconnect(smtp_adapter, smtp):
    logger = MagicMock()
    smtp_adapter.logger = logger
    smtp.send_message.side_effect = [
        SMTPServerDisconnected("Server disconnected"),
        None,
    ]

    await smtp_adapter.send_mail(MagicMock())

    assert smtp.send_message.await_count == 2
    logger.warning.assert_called_once_with("Reconnecting to SMTP server...")
    smtp.connect.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_mail_server_disconnected_no_reconnect(smtp_adapter, smtp):
    logger = MagicMock()
    smtp_adapter.logger = logger
    smtp.send_message.side_effect = [
        SMTPServerDisconnected("Server disconnected")
    ] * Settings.RETRY_COUNT

    await smtp_adapter.send_mail(MagicMock())

    assert smtp.send_message.await_count == Settings.RETRY_COUNT
    logger.error.assert_called_once_with(
        f"Could not send mail after {Settings.RETRY_COUNT} attempts"
    )
