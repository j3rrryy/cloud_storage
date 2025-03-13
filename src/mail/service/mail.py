from aiosmtplib import SMTP

from dto import BaseMailDTO, InfoMailDTO, ResetMailDTO, VerificationMailDTO
from mail import Sender, get_smtp


class MailService:
    _to_method = {
        VerificationMailDTO: Sender.verification,
        InfoMailDTO: Sender.info,
        ResetMailDTO: Sender.reset,
    }

    @classmethod
    @get_smtp
    async def send_email(cls, mail: type[BaseMailDTO], *, smtp: SMTP) -> None:
        await cls._to_method[type(mail)](mail, smtp)
