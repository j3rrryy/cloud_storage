from dto import mail_dto
from enums import MailTypes

from .base_service import KafkaBaseService


class MailService(KafkaBaseService):
    async def verification(
        self, verification_mail: mail_dto.VerificationMailDTO
    ) -> None:
        await self._producer.send(
            MailTypes.VERIFICATION.name, self.serialize_dto(verification_mail)
        )

    async def info(self, info_mail: mail_dto.InfoMailDTO) -> None:
        await self._producer.send(MailTypes.INFO.name, self.serialize_dto(info_mail))

    async def reset(self, reset_mail: mail_dto.ResetMailDTO) -> None:
        await self._producer.send(MailTypes.RESET.name, self.serialize_dto(reset_mail))
