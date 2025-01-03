from datetime import datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = sa.Column(
        UUID(as_uuid=False),
        unique=True,
        primary_key=True,
        default=uuid4,
    )
    username = sa.Column(sa.VARCHAR, unique=True, nullable=False)
    email = sa.Column(sa.VARCHAR, nullable=False, unique=True)
    password = sa.Column(sa.VARCHAR, nullable=False)
    verified = sa.Column(sa.BOOLEAN, default=False)
    registered = sa.Column(sa.TIMESTAMP, default=datetime.now)
    refresh_tokens = relationship("RefreshToken", back_populates="user")

    def __str__(self) -> str:
        return f"<User: {self.user_id}>"

    def columns_to_dict(self) -> dict:
        d = {key: getattr(self, key) for key in self.__mapper__.c.keys()}
        return d


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token_id = sa.Column(
        UUID(as_uuid=False),
        unique=True,
        primary_key=True,
        default=uuid4,
    )
    refresh_token = sa.Column(sa.VARCHAR, unique=True)
    user_id = sa.Column(
        UUID(as_uuid=False), sa.ForeignKey(User.user_id, ondelete="CASCADE")
    )
    user_ip = sa.Column(sa.VARCHAR, nullable=False)
    browser = sa.Column(sa.VARCHAR, nullable=True)
    last_accessed = sa.Column(sa.TIMESTAMP, default=datetime.now)
    user = relationship(User, back_populates="refresh_tokens")
    access_tokens = relationship("AccessToken", back_populates="refresh_token_parent")

    def __str__(self) -> str:
        return f"<RefreshToken: {self.refresh_token}>"

    def columns_to_dict(self) -> dict:
        d = {key: getattr(self, key) for key in self.__mapper__.c.keys()}
        return d


class AccessToken(Base):
    __tablename__ = "access_tokens"

    access_token = sa.Column(sa.VARCHAR, unique=True, primary_key=True)
    refresh_token = sa.Column(
        sa.VARCHAR, sa.ForeignKey(RefreshToken.refresh_token, ondelete="CASCADE")
    )
    refresh_token_parent = relationship(RefreshToken, back_populates="access_tokens")

    def __str__(self) -> str:
        return f"<AccessToken: {self.access_token}>"
