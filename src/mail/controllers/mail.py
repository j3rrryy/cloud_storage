from aiosmtplib import SMTP

from dto import BaseMailDTO, InfoMailDTO, ResetMailDTO, VerificationMailDTO
from mail import Mail


class MailController:
    _to_method = {
        VerificationMailDTO: Mail.verification,
        InfoMailDTO: Mail.info,
        ResetMailDTO: Mail.reset,
    }

    @classmethod
    async def send_email(cls, mail: type[BaseMailDTO], smtp: SMTP) -> None:
        await cls._to_method[type(mail)](mail, smtp)
