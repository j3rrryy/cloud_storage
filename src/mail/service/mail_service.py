import inject
from aiosmtplib import SMTP

from dto import BaseMailDTO, InfoMailDTO, ResetMailDTO, VerificationMailDTO
from mail import MailBuilder


class MailService:
    @staticmethod
    @inject.autoparams()
    async def send_email(mail: BaseMailDTO, smtp: SMTP) -> None:
        match mail:
            case VerificationMailDTO():
                msg = MailBuilder.verification(mail)
            case InfoMailDTO():
                msg = MailBuilder.info(mail)
            case ResetMailDTO():
                msg = MailBuilder.reset(mail)
            case _:
                raise ValueError(
                    f"{mail.__class__.__name__} is an unsupported mail type"
                )
        await smtp.send_message(msg)
