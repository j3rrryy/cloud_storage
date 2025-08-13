from unittest.mock import MagicMock, patch

import pytest

from dto import BaseMailDTO, InfoMailDTO, ResetMailDTO, VerificationMailDTO
from mail import MailBuilder
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
async def test_send_email_parametrized(mail, attr_name, mock_smtp):
    mock_verification = MagicMock(return_value="verification")
    mock_info = MagicMock(return_value="info")
    mock_reset = MagicMock(return_value="reset")

    with (
        patch.object(MailBuilder, "verification", mock_verification),
        patch.object(MailBuilder, "info", mock_info),
        patch.object(MailBuilder, "reset", mock_reset),
    ):
        await MailService.send_email(mail)  # type: ignore
        getattr(locals()[f"mock_{attr_name}"], "assert_called_once_with")(mail)
        mock_smtp.send_message.assert_awaited_once_with(attr_name)


@pytest.mark.asyncio
async def test_send_email_exception(mock_smtp):
    class UnknownMailDTO(BaseMailDTO): ...

    with pytest.raises(ValueError, match="UnknownMailDTO is an unsupported mail type"):
        await MailService.send_email(UnknownMailDTO(USERNAME, EMAIL))  # type: ignore
