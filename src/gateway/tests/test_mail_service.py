import pytest

from services import Mail
from utils import MailTypes

from .mocks import BROWSER, CODE, EMAIL, USER_IP, USERNAME, VERIFICATION_TOKEN


@pytest.mark.asyncio
async def test_register(mail_service: Mail):
    data = {
        "verification_token": VERIFICATION_TOKEN,
        "username": USERNAME,
        "email": EMAIL,
    }
    await mail_service.register(data)
    mail_service._producer.send.assert_called_once_with(
        MailTypes.VERIFICATION.name, mail_service.serialize_dict(data)
    )


@pytest.mark.asyncio
async def test_request_reset_code(mail_service: Mail):
    data = {"username": USERNAME, "email": EMAIL, "code": CODE}
    await mail_service.request_reset_code(data)
    mail_service._producer.send.assert_called_once_with(
        MailTypes.RESET.name, mail_service.serialize_dict(data)
    )


@pytest.mark.asyncio
async def test_log_in(mail_service: Mail):
    data = {
        "username": USERNAME,
        "email": EMAIL,
        "user_ip": USER_IP,
        "browser": BROWSER,
    }
    await mail_service.log_in(data)
    mail_service._producer.send.assert_called_once_with(
        MailTypes.INFO.name, mail_service.serialize_dict(data)
    )


@pytest.mark.asyncio
async def test_resend_verification_mail(mail_service: Mail):
    data = {
        "verification_token": VERIFICATION_TOKEN,
        "username": USERNAME,
        "email": EMAIL,
    }
    await mail_service.resend_verification_mail(data)
    mail_service._producer.send.assert_called_once_with(
        MailTypes.VERIFICATION.name, mail_service.serialize_dict(data)
    )


@pytest.mark.asyncio
async def test_update_email(mail_service: Mail):
    data = {
        "verification_token": VERIFICATION_TOKEN,
        "username": USERNAME,
        "email": EMAIL,
    }
    await mail_service.update_email(data)
    mail_service._producer.send.assert_called_once_with(
        MailTypes.VERIFICATION.name, mail_service.serialize_dict(data)
    )
