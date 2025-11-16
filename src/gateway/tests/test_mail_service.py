import pytest

from adapters import MailKafkaAdapter
from dto import mail_dto
from enums import MailTypes

from .mocks import BROWSER, CODE, EMAIL, USER_IP, USERNAME, VERIFICATION_TOKEN


@pytest.mark.asyncio
async def test_verification(mail_service: MailKafkaAdapter):
    dto = mail_dto.VerificationMailDTO(
        verification_token=VERIFICATION_TOKEN, username=USERNAME, email=EMAIL
    )

    await mail_service.verification(dto)

    mail_service._producer.send.assert_awaited_once_with(
        MailTypes.VERIFICATION.name, dto.to_msgpack()
    )


@pytest.mark.asyncio
async def test_info(mail_service: MailKafkaAdapter):
    dto = mail_dto.InfoMailDTO(
        username=USERNAME, email=EMAIL, user_ip=USER_IP, browser=BROWSER
    )

    await mail_service.info(dto)

    mail_service._producer.send.assert_awaited_once_with(
        MailTypes.INFO.name, dto.to_msgpack()
    )


@pytest.mark.asyncio
async def test_reset(mail_service: MailKafkaAdapter):
    dto = mail_dto.ResetMailDTO(code=CODE, username=USERNAME, email=EMAIL)

    await mail_service.reset(dto)

    mail_service._producer.send.assert_awaited_once_with(
        MailTypes.RESET.name, dto.to_msgpack()
    )
