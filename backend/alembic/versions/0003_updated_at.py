"""add updated_at column

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-26

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "listings",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    # Backfill existing rows to their created_at so "last modified" is sensible.
    op.execute("UPDATE listings SET updated_at = created_at")


def downgrade() -> None:
    op.drop_column("listings", "updated_at")
