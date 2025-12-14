from enum import Enum

from dto import InfoMailDTO, ResetMailDTO, VerificationMailDTO


class MailTypes(Enum):
    VERIFICATION = VerificationMailDTO
    INFO = InfoMailDTO
    RESET = ResetMailDTO
