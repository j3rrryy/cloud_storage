import pytest

from dto import mail_dto
from enums import MailTypes

from .mocks import BROWSER, CODE, EMAIL, USER_IP, USERNAME, VERIFICATION_TOKEN


@pytest.mark.asyncio
async def test_verification(mail_service_v1):
    dto = mail_dto.VerificationMailDTO(
        verification_token=VERIFICATION_TOKEN, username=USERNAME, email=EMAIL
    )

    await mail_service_v1.verification(dto)

    mail_service_v1._producer.send.assert_awaited_once_with(
        MailTypes.VERIFICATION.name, dto.to_msgpack()
    )


@pytest.mark.asyncio
async def test_info(mail_service_v1):
    dto = mail_dto.InfoMailDTO(
        username=USERNAME, email=EMAIL, user_ip=USER_IP, browser=BROWSER
    )

    await mail_service_v1.info(dto)

    mail_service_v1._producer.send.assert_awaited_once_with(
        MailTypes.INFO.name, dto.to_msgpack()
    )


@pytest.mark.asyncio
async def test_reset(mail_service_v1):
    dto = mail_dto.ResetMailDTO(code=CODE, username=USERNAME, email=EMAIL)

    await mail_service_v1.reset(dto)

    mail_service_v1._producer.send.assert_awaited_once_with(
        MailTypes.RESET.name, dto.to_msgpack()
    )
