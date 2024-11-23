import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class File(Base):
    __tablename__ = "files"

    file_id = sa.Column(
        UUID(as_uuid=False),
        unique=True,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id = sa.Column(UUID(as_uuid=False), nullable=False)
    name = sa.Column(sa.VARCHAR, unique=True, nullable=False)
    size = sa.Column(sa.BIGINT, nullable=True)
    uploaded = sa.Column(sa.TIMESTAMP, default=datetime.now)

    def __str__(self) -> str:
        return f"<File: {self.file_id}>"

    def columns_to_dict(self) -> dict:
        d = {key: getattr(self, key) for key in self.__mapper__.c.keys()}
        return d
