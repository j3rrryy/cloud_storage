from enum import Enum


class TokenType(Enum):
    ACCESS = 0
    REFRESH = 1
    EMAIL_CONFIRMATION = 2


class ResetCodeStatus(Enum):
    VALIDATED = "validated"
