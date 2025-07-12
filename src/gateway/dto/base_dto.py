from dataclasses import asdict as dc_asdict
from dataclasses import dataclass
from typing import Any, Type, TypeVar

from msgspec import Struct
from msgspec.structs import asdict as ms_asdict

T = TypeVar("T", bound="BaseDTO")


@dataclass(slots=True, frozen=True)
class BaseDTO:
    def dict(self) -> dict[str, Any]:
        return dc_asdict(self)

    @classmethod
    def from_struct(cls: Type[T], struct: Struct) -> T:
        return cls(**ms_asdict(struct))
