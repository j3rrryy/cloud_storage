from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class BaseMailDTO:
    locale: str
    username: str
    email: str
