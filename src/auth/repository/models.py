from datetime import datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

from utils import utc_now_naive

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(UUID(False), primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(sa.String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    email_confirmed: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, default=False
    )
    registered_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP, nullable=False, default=utc_now_naive
    )

    tokens: Mapped[list["TokenPair"]] = relationship(
        "TokenPair", back_populates="user", passive_deletes=True
    )


class TokenPair(Base):
    __tablename__ = "tokens"

    session_id: Mapped[str] = mapped_column(
        UUID(False), primary_key=True, default=uuid4
    )
    user_id: Mapped[str] = mapped_column(
        sa.ForeignKey(User.user_id, ondelete="CASCADE"), index=True, nullable=False
    )
    access_token: Mapped[str] = mapped_column(sa.CHAR(64), unique=True, nullable=False)
    refresh_token: Mapped[str] = mapped_column(sa.CHAR(64), unique=True, nullable=False)
    user_ip: Mapped[str] = mapped_column(sa.String(45), nullable=False)
    browser: Mapped[str] = mapped_column(sa.String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP, index=True, nullable=False, default=utc_now_naive
    )

    user: Mapped[User] = relationship(
        User, back_populates="tokens", passive_deletes=True
    )
