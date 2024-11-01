"""initial

Revision ID: 0aa78703552c
Revises:
Create Date: 2024-07-22 12:32:14.688040

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0aa78703552c"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "files",
        sa.Column("file_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("path", sa.VARCHAR(), nullable=True),
        sa.Column("name", sa.VARCHAR(), nullable=True),
        sa.Column("size", sa.VARCHAR(), nullable=False),
        sa.Column("uploaded", sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("file_id"),
        sa.UniqueConstraint("file_id"),
        sa.UniqueConstraint("path"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("files")
    # ### end Alembic commands ###