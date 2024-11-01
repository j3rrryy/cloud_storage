from aiosmtplib import SMTP

from mail import Mail
from utils import MailTypes


class MailController:
    @classmethod
    async def send_email(
        cls, message: dict[str, str], mail_type: MailTypes, smtp: SMTP
    ) -> None:
        match mail_type:
            case MailTypes.VERIFICATION:
                await Mail.verification(message, smtp)
            case MailTypes.INFO:
                await Mail.info(message, smtp)
