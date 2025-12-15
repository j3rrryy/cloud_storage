from unittest.mock import MagicMock

import pytest


@pytest.mark.asyncio
async def test_send_mail(smtp_adapter, smtp):
    mock_mail = MagicMock()

    await smtp_adapter.send_mail(mock_mail)

    smtp.send_message.assert_awaited_once_with(mock_mail)
