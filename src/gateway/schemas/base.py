from typing import Any

from msgspec import Struct


class BaseStruct(Struct):
    def to_dict(self) -> dict[str, Any]:
        return {field: getattr(self, field) for field in self.__struct_fields__}
