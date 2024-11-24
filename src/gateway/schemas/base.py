from typing import Any
from uuid import UUID

from msgspec import Struct


class BaseStruct(Struct):
    def to_dict(self) -> dict[str, Any]:
        result = {}

        for field in self.__struct_fields__:
            if isinstance(value := getattr(self, field), UUID):
                result[field] = str(value)
            else:
                result[field] = value

        return result
