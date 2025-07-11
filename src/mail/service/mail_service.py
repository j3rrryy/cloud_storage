from dto import BaseMailDTO, InfoMailDTO, ResetMailDTO, VerificationMailDTO
from mail import MailSender


class MailService:
    @classmethod
    async def send_email(cls, mail: BaseMailDTO) -> None:
        match mail:
            case VerificationMailDTO():
                await MailSender.verification(mail)  # type: ignore
            case InfoMailDTO():
                await MailSender.info(mail)  # type: ignore
            case ResetMailDTO():
                await MailSender.reset(mail)  # type: ignore
            case _:
                raise ValueError(
                    f"{mail.__class__.__name__} is an unsupported mail type"
                )
