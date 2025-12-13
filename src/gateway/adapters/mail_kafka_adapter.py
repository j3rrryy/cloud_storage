from dto import mail_dto
from enums import MailTypes
from protocols import MailServiceProtocol

from .base_adapter import BaseKafkaAdapter


class MailKafkaAdapter(BaseKafkaAdapter, MailServiceProtocol):
    async def verification(
        self, verification_mail: mail_dto.VerificationMailDTO
    ) -> None:
        await self._producer.send(
            MailTypes.VERIFICATION.name, verification_mail.to_msgpack()
        )

    async def info(self, info_mail: mail_dto.InfoMailDTO) -> None:
        await self._producer.send(MailTypes.INFO.name, info_mail.to_msgpack())

    async def reset(self, reset_mail: mail_dto.ResetMailDTO) -> None:
        await self._producer.send(MailTypes.RESET.name, reset_mail.to_msgpack())
