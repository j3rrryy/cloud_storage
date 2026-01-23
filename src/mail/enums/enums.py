from enum import Enum


class MailType(Enum):
    EMAIL_CONFIRMATION = 0
    NEW_LOGIN = 1
    PASSWORD_RESET = 2
