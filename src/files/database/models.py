from datetime import datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class File(BaseModel):
    __tablename__ = "files"

    id: Mapped[str] = mapped_column(
        UUID(False), primary_key=True, unique=True, default=uuid4
    )
    user_id: Mapped[str] = mapped_column(UUID(False), nullable=False)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    path: Mapped[str] = mapped_column(sa.String, unique=True, nullable=False)
    size: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    uploaded: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP, nullable=False, default=datetime.now
    )

    def __str__(self) -> str:
        return f"<File: {self.name}>"
