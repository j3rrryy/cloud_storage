from datetime import datetime, timezone
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()


class File(Base):
    __tablename__ = "files"

    file_id: Mapped[str] = mapped_column(
        UUID(False), primary_key=True, unique=True, default=uuid4
    )
    user_id: Mapped[str] = mapped_column(UUID(False), index=True, nullable=False)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    path: Mapped[str] = mapped_column(sa.String(512), unique=True, nullable=False)
    size: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def __str__(self) -> str:
        return f"<File: {self.file_id}>"
