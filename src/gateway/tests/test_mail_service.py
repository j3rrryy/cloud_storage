import pytest

from dto import mail_dto
from enums import MailTypes

from .mocks import BROWSER, CODE, EMAIL, USER_IP, USERNAME, VERIFICATION_TOKEN


@pytest.mark.asyncio
async def test_verification(mail_service):
    dto = mail_dto.VerificationMailDTO(
        verification_token=VERIFICATION_TOKEN, username=USERNAME, email=EMAIL
    )
    await mail_service.verification(dto)
    mail_service._producer.send.assert_called_once_with(
        MailTypes.VERIFICATION.name, mail_service.serialize_dict(dto.dict())
    )


@pytest.mark.asyncio
async def test_info(mail_service):
    dto = mail_dto.InfoMailDTO(
        username=USERNAME, email=EMAIL, user_ip=USER_IP, browser=BROWSER
    )
    await mail_service.info(dto)
    mail_service._producer.send.assert_called_once_with(
        MailTypes.INFO.name, mail_service.serialize_dict(dto.dict())
    )


@pytest.mark.asyncio
async def test_reset(mail_service):
    dto = mail_dto.ResetMailDTO(code=CODE, username=USERNAME, email=EMAIL)
    await mail_service.reset(dto)
    mail_service._producer.send.assert_called_once_with(
        MailTypes.RESET.name, mail_service.serialize_dict(dto.dict())
    )
