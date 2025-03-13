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
async def test_send_email_parametrized(mail, smtp):
    mock_method = AsyncMock()

    with patch.object(MailService, "_to_method", {type(mail): mock_method}):
        await MailService.send_email(mail, smtp)
        mock_method.assert_awaited_once_with(mail, smtp)
