from dto import mail
from utils import MailTypes

from .base import KafkaBase


class Mail(KafkaBase):
    async def verification(self, verification_mail: mail.VerificationMailDTO) -> None:
        await self._producer.send(
            MailTypes.VERIFICATION.name, self.serialize_dict(verification_mail.dict())
        )

    async def info(self, info_mail: mail.InfoMailDTO) -> None:
        await self._producer.send(
            MailTypes.INFO.name, self.serialize_dict(info_mail.dict())
        )

    async def reset(self, reset_mail: mail.ResetMailDTO) -> None:
        await self._producer.send(
            MailTypes.RESET.name, self.serialize_dict(reset_mail.dict())
        )
