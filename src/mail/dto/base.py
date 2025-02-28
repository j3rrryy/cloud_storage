from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class BaseMailDTO:
    username: str
    email: str
