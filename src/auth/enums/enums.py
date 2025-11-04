from enum import Enum


class TokenTypes(Enum):
    ACCESS = 0
    REFRESH = 1
    VERIFICATION = 2


class ResetCodeStatus(Enum):
    VALIDATED = "validated"
