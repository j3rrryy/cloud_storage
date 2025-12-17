import pytest

from dto import BaseMailDTO, LoginMailDTO, ResetMailDTO, VerificationMailDTO

from ..mocks import BROWSER, CODE, EMAIL, USER_IP, USERNAME, VERIFICATION_TOKEN


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "dto",
    [
        VerificationMailDTO(USERNAME, EMAIL, VERIFICATION_TOKEN),
        LoginMailDTO(USERNAME, EMAIL, USER_IP, BROWSER),
        ResetMailDTO(USERNAME, EMAIL, CODE),
    ],
)
async def test_send_mail(dto, smtp_facade, smtp):
    await smtp_facade.send_mail(dto)

    smtp.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_mail_no_strategy_found(smtp_facade):
    class UnknownMailDTO(BaseMailDTO):
        pass

    dto = UnknownMailDTO(USERNAME, EMAIL)

    with pytest.raises(
        ValueError, match=f"No strategy found for {UnknownMailDTO.__name__}"
    ):
        await smtp_facade.send_mail(dto)
