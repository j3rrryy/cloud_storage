from datetime import datetime
from typing import Optional
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()


class Folder(Base):
    __tablename__ = "folders"

    folder_id: Mapped[str] = mapped_column(UUID(False), primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(
        UUID(False), index=True, nullable=False, server_default=""
    )
    parent_id: Mapped[Optional[str]] = mapped_column(
        UUID(False),
        sa.ForeignKey("folders.folder_id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)

    parent: Mapped[Optional["Folder"]] = relationship(
        "Folder",
        back_populates="subfolders",
        passive_deletes=True,
        remote_side=[folder_id],
    )
    subfolders: Mapped[list["Folder"]] = relationship("Folder", back_populates="parent")
    files: Mapped[list["File"]] = relationship("File", back_populates="folder")

    __table_args__ = (
        sa.UniqueConstraint(user_id, parent_id, name),
        sa.Index("ix_folders_folder_id_user_id", folder_id, user_id),
        sa.Index(
            "ix_folders_parent_id_user_id_name_folder_id",
            "parent_id",
            "user_id",
            "name",
            "folder_id",
        ),
    )

    def __str__(self) -> str:
        return f"<Folder: {self.folder_id}>"


class File(Base):
    __tablename__ = "files"

    file_id: Mapped[str] = mapped_column(UUID(False), primary_key=True, default=uuid4)
    folder_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey(Folder.folder_id, ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    size: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )

    folder: Mapped[Folder] = relationship(
        Folder, back_populates="files", passive_deletes=True
    )

    __table_args__ = (
        sa.UniqueConstraint(folder_id, name),
        sa.Index("ix_files_folder_id_name_file_id", "folder_id", "name", "file_id"),
    )

    def __str__(self) -> str:
        return f"<File: {self.file_id}>"
