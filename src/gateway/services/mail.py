from utils import MailTypes

from .base import KafkaBase


class Mail(KafkaBase):
    async def register(self, verification_mail: dict[str, str]) -> None:
        await self._producer.send(
            MailTypes.VERIFICATION.name, self.serialize_dict(verification_mail)
        )

    async def log_in(self, info_mail: dict[str, str]) -> None:
        await self._producer.send(MailTypes.INFO.name, self.serialize_dict(info_mail))

    async def resend_verification_mail(self, verification_mail: dict[str, str]) -> None:
        await self._producer.send(
            MailTypes.VERIFICATION.name, self.serialize_dict(verification_mail)
        )

    async def update_email(self, verification_mail: dict[str, str]) -> None:
        await self._producer.send(
            MailTypes.VERIFICATION.name, self.serialize_dict(verification_mail)
        )
