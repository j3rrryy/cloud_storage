from unittest.mock import AsyncMock, patch

import pytest

from dto import BaseMailDTO, InfoMailDTO, ResetMailDTO, VerificationMailDTO
from mail import MailSender
from service import MailService

from .mocks import BROWSER, CODE, EMAIL, USER_IP, USERNAME, VERIFICATION_TOKEN


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mail, attr_name",
    (
        (VerificationMailDTO(USERNAME, EMAIL, VERIFICATION_TOKEN), "verification"),
        (InfoMailDTO(USERNAME, EMAIL, USER_IP, BROWSER), "info"),
        (ResetMailDTO(USERNAME, EMAIL, CODE), "reset"),
    ),
)
async def test_send_email_parametrized(mail, attr_name):
    mock_verification = AsyncMock()
    mock_info = AsyncMock()
    mock_reset = AsyncMock()

    with (
        patch.object(MailSender, "verification", mock_verification),
        patch.object(MailSender, "info", mock_info),
        patch.object(MailSender, "reset", mock_reset),
    ):
        await MailService.send_email(mail)
        getattr(locals()[f"mock_{attr_name}"], "assert_awaited_once_with")(mail)


@pytest.mark.asyncio
async def test_send_email_exception():
    class UnknownMailDTO(BaseMailDTO): ...

    with pytest.raises(ValueError, match="UnknownMailDTO is an unsupported mail type"):
        await MailService.send_email(UnknownMailDTO(USERNAME, EMAIL))
