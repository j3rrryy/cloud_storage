from datetime import datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(False), primary_key=True, unique=True, default=uuid4
    )
    username: Mapped[str] = mapped_column(sa.String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(sa.String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(sa.String, nullable=False)
    verified: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)
    registered: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP, nullable=False, default=datetime.now
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user"
    )

    def __str__(self) -> str:
        return f"<User: {self.username}>"


class AccessToken(BaseModel):
    __tablename__ = "access_tokens"

    access_token: Mapped[str] = mapped_column(sa.String, primary_key=True, unique=True)
    refresh_token: Mapped[str] = mapped_column(
        sa.ForeignKey("refresh_tokens.refresh_token", ondelete="CASCADE"),
        nullable=False,
    )

    refresh_token_parent: Mapped["RefreshToken"] = relationship(
        "RefreshToken", back_populates="access_tokens"
    )

    def __str__(self) -> str:
        return f"<AccessToken: {self.access_token}>"


class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(
        UUID(False), primary_key=True, unique=True, default=uuid4
    )
    refresh_token: Mapped[str] = mapped_column(sa.String, unique=True, nullable=False)
    user_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey(User.id, ondelete="CASCADE"), nullable=False
    )
    user_ip: Mapped[str] = mapped_column(sa.String, nullable=False)
    browser: Mapped[str] = mapped_column(sa.String, nullable=False)
    last_accessed: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP, nullable=False, default=datetime.now
    )

    user: Mapped[User] = relationship(User, back_populates="refresh_tokens")
    access_tokens: Mapped[list["AccessToken"]] = relationship(
        AccessToken, back_populates="refresh_token_parent"
    )

    def __str__(self) -> str:
        return f"<RefreshToken: {self.refresh_token}>"
