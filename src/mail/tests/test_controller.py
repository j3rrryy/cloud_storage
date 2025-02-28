from unittest.mock import AsyncMock, patch

import pytest

from controllers import MailController
from dto import InfoMailDTO, ResetMailDTO, VerificationMailDTO

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

    with patch.object(MailController, "_to_method", {type(mail): mock_method}):
        await MailController.send_email(mail, smtp)
        mock_method.assert_awaited_once_with(mail, smtp)
