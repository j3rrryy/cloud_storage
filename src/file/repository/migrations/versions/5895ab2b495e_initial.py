"""initial

Revision ID: 5895ab2b495e
Revises:
Create Date: 2025-09-03 19:44:10.210406

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5895ab2b495e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "folders",
        sa.Column("folder_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("parent_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False, server_default=""),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["folders.folder_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("folder_id"),
        sa.UniqueConstraint("user_id", "parent_id", "name"),
    )
    op.create_index(
        "ix_folders_folder_id_user_id",
        "folders",
        ["folder_id", "user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_folders_parent_id"), "folders", ["parent_id"], unique=False
    )
    op.create_index(
        "ix_folders_parent_id_user_id_name_folder_id",
        "folders",
        ["parent_id", "user_id", "name", "folder_id"],
        unique=False,
    )
    op.create_index(op.f("ix_folders_user_id"), "folders", ["user_id"], unique=False)
    op.create_table(
        "files",
        sa.Column("file_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("folder_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("size", sa.BigInteger(), nullable=False),
        sa.Column(
            "uploaded_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["folder_id"], ["folders.folder_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("file_id"),
        sa.UniqueConstraint("folder_id", "name"),
    )
    op.create_index(op.f("ix_files_folder_id"), "files", ["folder_id"], unique=False)
    op.create_index(
        "ix_files_folder_id_name_file_id",
        "files",
        ["folder_id", "name", "file_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_files_folder_id_name_file_id", table_name="files")
    op.drop_index(op.f("ix_files_folder_id"), table_name="files")
    op.drop_table("files")
    op.drop_index(op.f("ix_folders_user_id"), table_name="folders")
    op.drop_index("ix_folders_parent_id_user_id_name_folder_id", table_name="folders")
    op.drop_index(op.f("ix_folders_parent_id"), table_name="folders")
    op.drop_index("ix_folders_folder_id_user_id", table_name="folders")
    op.drop_table("folders")
