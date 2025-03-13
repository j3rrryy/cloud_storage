from unittest.mock import AsyncMock, patch

import pytest

from dto import InfoMailDTO, ResetMailDTO, VerificationMailDTO
from service import MailService

from .mocks import BROWSER, CODE, EMAIL, USER_IP, USERNAME, VERIFICATION_TOKEN


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mail",
    (
        VerificationMailDTO(USERNAME, EMAIL, VERIFICATION_TOKEN),
        InfoMailDTO(USERNAME, EMAIL, USER_IP, BROWSER),
        ResetMailDTO(USERNAME, EMAIL, CODE),
    ),
)
@patch("mail.engine._smtp")
async def test_send_email_parametrized(mock_smtp, mail):
    smtp = AsyncMock()
    mock_method = AsyncMock()
    mock_smtp.__aenter__.return_value = smtp

    with patch.object(MailService, "_to_method", {type(mail): mock_method}):
        await MailService.send_email(mail)  # type: ignore
        mock_method.assert_awaited_once_with(mail, smtp)
