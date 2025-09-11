"""initial

Revision ID: 7b8c27dc79cf
Revises:
Create Date: 2025-09-02 20:38:22.320731

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7b8c27dc79cf"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("username", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=128), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False),
        sa.Column(
            "registered_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "tokens",
        sa.Column("session_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("access_token", sa.String(length=350), nullable=False),
        sa.Column("refresh_token", sa.String(length=350), nullable=False),
        sa.Column("user_ip", sa.String(length=45), nullable=False),
        sa.Column("browser", sa.String(length=150), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("session_id"),
        sa.UniqueConstraint("access_token"),
        sa.UniqueConstraint("refresh_token"),
    )
    op.create_index(
        op.f("ix_tokens_created_at"), "tokens", ["created_at"], unique=False
    )
    op.create_index(op.f("ix_tokens_user_id"), "tokens", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_tokens_user_id"), table_name="tokens")
    op.drop_index(op.f("ix_tokens_created_at"), table_name="tokens")
    op.drop_table("tokens")
    op.drop_table("users")
