from typing import Any

from enums import MailType

from .base_dto import BaseMailDTO
from .dto import EmailConfirmationMailDTO, NewLoginMailDTO, PasswordResetMailDTO


class MessageToDTOConverter:
    _dto_classes: dict[MailType, type[BaseMailDTO]] = {
        MailType.EMAIL_CONFIRMATION: EmailConfirmationMailDTO,
        MailType.NEW_LOGIN: NewLoginMailDTO,
        MailType.PASSWORD_RESET: PasswordResetMailDTO,
    }

    @classmethod
    def convert(cls, topic: str, message: dict[str, Any]) -> BaseMailDTO:
        try:
            mail_type = MailType[topic]
            dto_cls = cls._dto_classes[mail_type]
            return dto_cls(**message)
        except KeyError:
            raise ValueError(f"Unsupported mail type: {topic}")
        except TypeError as exc:
            raise ValueError(f"Invalid message data for {topic}: {exc}")
