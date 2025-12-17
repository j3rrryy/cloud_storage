from aiokafka import AIOKafkaProducer

from dto import mail_dto
from enums import MailTypes
from protocols import MailServiceProtocol


class MailKafkaAdapter(MailServiceProtocol):
    def __init__(self, producer: AIOKafkaProducer):
        self._producer = producer

    async def email_confirmation(
        self, email_confirmation_mail: mail_dto.EmailConfirmationMailDTO
    ) -> None:
        await self._producer.send(
            MailTypes.EMAIL_CONFIRMATION.name, email_confirmation_mail.to_msgpack()
        )

    async def new_login(self, new_login_mail: mail_dto.NewLoginMailDTO) -> None:
        await self._producer.send(MailTypes.NEW_LOGIN.name, new_login_mail.to_msgpack())

    async def password_reset(
        self, password_reset_mail: mail_dto.PasswordResetMailDTO
    ) -> None:
        await self._producer.send(
            MailTypes.PASSWORD_RESET.name, password_reset_mail.to_msgpack()
        )
