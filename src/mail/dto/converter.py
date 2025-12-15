from typing import Any

from enums import MailTypes

from .base_dto import BaseMailDTO
from .dto import InfoMailDTO, ResetMailDTO, VerificationMailDTO


class MessageToDTOConverter:
    _dto_classes: dict[MailTypes, type[BaseMailDTO]] = {
        MailTypes.VERIFICATION: VerificationMailDTO,
        MailTypes.INFO: InfoMailDTO,
        MailTypes.RESET: ResetMailDTO,
    }

    @classmethod
    def convert(cls, topic: str, message: dict[str, Any]) -> BaseMailDTO:
        try:
            mail_type = MailTypes[topic]
            dto_cls = cls._dto_classes[mail_type]
            return dto_cls(**message)
        except KeyError:
            raise ValueError(f"Unsupported mail type: {topic}")
        except TypeError as exc:
            raise ValueError(f"Invalid message data for {topic}: {exc}")
