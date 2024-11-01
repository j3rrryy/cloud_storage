"""initial

Revision ID: 15a4857de5bf
Revises:
Create Date: 2024-07-31 19:20:04.328515

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "15a4857de5bf"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("username", sa.VARCHAR(), nullable=False),
        sa.Column("email", sa.VARCHAR(), nullable=False),
        sa.Column("password", sa.VARCHAR(), nullable=False),
        sa.Column("verified", sa.BOOLEAN(), nullable=True),
        sa.Column("registered", sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("user_id"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("token_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("refresh_token", sa.VARCHAR(), nullable=True),
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("user_ip", sa.VARCHAR(), nullable=False),
        sa.Column("browser", sa.VARCHAR(), nullable=True),
        sa.Column("last_accessed", sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("token_id"),
        sa.UniqueConstraint("refresh_token"),
        sa.UniqueConstraint("token_id"),
    )
    op.create_table(
        "access_tokens",
        sa.Column("access_token", sa.VARCHAR(), nullable=False),
        sa.Column("refresh_token", sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(
            ["refresh_token"], ["refresh_tokens.refresh_token"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("access_token"),
        sa.UniqueConstraint("access_token"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("access_tokens")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
    # ### end Alembic commands ###
