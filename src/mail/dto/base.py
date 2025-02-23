import pickle
from dataclasses import dataclass

from aiokafka import ConsumerRecord

from utils import MailTypes

from .dto import InfoMailDTO, ResetMailDTO, VerificationMailDTO


@dataclass(slots=True, frozen=True)
class BaseMailDTO:
    username: str
    email: str


class DTOFactory:
    _converted_mails = {
        MailTypes.VERIFICATION: VerificationMailDTO,
        MailTypes.INFO: InfoMailDTO,
        MailTypes.RESET: ResetMailDTO,
    }

    @classmethod
    def from_message(cls, message: ConsumerRecord) -> type[BaseMailDTO]:
        if message.value is None:
            raise ValueError("The message is empty")

        mail = pickle.loads(message.value)
        mail_type = MailTypes[message.topic]
        return cls._converted_mails[mail_type](**mail)
