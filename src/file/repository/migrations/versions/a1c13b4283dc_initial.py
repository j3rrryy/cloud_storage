"""initial

Revision ID: a1c13b4283dc
Revises:
Create Date: 2025-03-30 23:38:40.495643

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1c13b4283dc"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "files",
        sa.Column("file_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("path", sa.String(length=512), nullable=False),
        sa.Column("size", sa.BigInteger(), nullable=False),
        sa.Column("uploaded_at", sa.TIMESTAMP(), nullable=False),
        sa.PrimaryKeyConstraint("file_id"),
        sa.UniqueConstraint("file_id"),
        sa.UniqueConstraint("path"),
    )
    op.create_index(op.f("ix_files_user_id"), "files", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_files_user_id"), table_name="files")
    op.drop_table("files")
