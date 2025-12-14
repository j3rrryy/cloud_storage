from typing import Any

from enums import MailTypes

from .base_dto import BaseMailDTO


class MessageToDTOConverter:
    @staticmethod
    def convert(topic: str, message: dict[str, Any]) -> BaseMailDTO:
        try:
            dto_class = MailTypes[topic].value
            return dto_class(**message)
        except KeyError:
            raise ValueError(f"Unsupported mail type: {topic}")
        except TypeError as exc:
            raise ValueError(f"Invalid message data for {topic}: {exc}")
