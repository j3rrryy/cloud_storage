"""initial

Revision ID: 85ab058be4b4
Revises:
Create Date: 2025-03-30 23:29:09.145605

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "85ab058be4b4"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("username", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=60), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False),
        sa.Column("registered_at", sa.TIMESTAMP(), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_table(
        "tokens",
        sa.Column("session_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("access_token", sa.String(length=350), nullable=False),
        sa.Column("refresh_token", sa.String(length=350), nullable=False),
        sa.Column("user_ip", sa.String(length=15), nullable=False),
        sa.Column("browser", sa.String(length=150), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("session_id"),
        sa.UniqueConstraint("session_id"),
    )
    op.create_index(
        op.f("ix_tokens_access_token"), "tokens", ["access_token"], unique=True
    )
    op.create_index(
        op.f("ix_tokens_refresh_token"), "tokens", ["refresh_token"], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_tokens_refresh_token"), table_name="tokens")
    op.drop_index(op.f("ix_tokens_access_token"), table_name="tokens")
    op.drop_table("tokens")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
