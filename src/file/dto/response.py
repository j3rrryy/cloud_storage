import datetime
from dataclasses import dataclass

from .base import BaseResponseDTO


@dataclass(slots=True, frozen=True)
class FileInfoResponseDTO(BaseResponseDTO):
    file_id: str
    user_id: str
    name: str
    size: int
    uploaded_at: datetime.datetime
