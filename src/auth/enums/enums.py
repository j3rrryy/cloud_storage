from enum import Enum


class TokenTypes(Enum):
    ACCESS = 0
    REFRESH = 1
    EMAIL_CONFIRMATION = 2


class ResetCodeStatus(Enum):
    VALIDATED = "validated"
