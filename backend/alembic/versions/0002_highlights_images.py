"""add highlights and images columns

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-26

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# JSONB on Postgres (matches the model's portable JSON type).
_JSON = postgresql.JSONB()


def upgrade() -> None:
    op.add_column("listings", sa.Column("highlights", _JSON, nullable=True))
    op.add_column("listings", sa.Column("images", _JSON, nullable=True))


def downgrade() -> None:
    op.drop_column("listings", "images")
    op.drop_column("listings", "highlights")
