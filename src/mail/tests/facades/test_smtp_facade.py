import pytest

from dto import (
    BaseMailDTO,
    EmailConfirmationMailDTO,
    NewLoginMailDTO,
    PasswordResetMailDTO,
)

from ..mocks import BROWSER, CODE, EMAIL, TOKEN, USER_IP, USERNAME


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "dto",
    [
        EmailConfirmationMailDTO(USERNAME, EMAIL, TOKEN),
        NewLoginMailDTO(USERNAME, EMAIL, USER_IP, BROWSER),
        PasswordResetMailDTO(USERNAME, EMAIL, CODE),
    ],
)
async def test_send_mail(dto, smtp_facade, smtp):
    await smtp_facade.send_mail(dto)

    smtp.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_mail_no_renderer_found(smtp_facade):
    class UnknownMailDTO(BaseMailDTO):
        pass

    dto = UnknownMailDTO(USERNAME, EMAIL)

    with pytest.raises(
        ValueError, match=f"No renderer found for {UnknownMailDTO.__name__}"
    ):
        await smtp_facade.send_mail(dto)
