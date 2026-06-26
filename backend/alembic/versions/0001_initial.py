"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-25

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(16), nullable=False),
        sa.Column("provider_id", sa.String(128), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.String(1024), nullable=True),
        sa.Column("role", sa.String(16), nullable=False, server_default="user"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("provider", "provider_id", name="uq_user_provider"),
    )

    op.create_table(
        "listings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(16), nullable=False),
        sa.Column("source_url", sa.String(1024), nullable=True),
        sa.Column("title", sa.String(512), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending_review"),
        sa.Column("intent", sa.String(16), nullable=True),
        sa.Column("has_room", sa.Boolean(), nullable=True),
        sa.Column("mbti", sa.String(8), nullable=True),
        sa.Column("has_pets", sa.Boolean(), nullable=True),
        sa.Column("pets_note", sa.String(255), nullable=True),
        sa.Column("budget_min", sa.Integer(), nullable=True),
        sa.Column("budget_max", sa.Integer(), nullable=True),
        sa.Column("area", sa.String(128), nullable=True),
        sa.Column("move_in_date", sa.Date(), nullable=True),
        sa.Column("gender_pref", sa.String(32), nullable=True),
        sa.Column("extracted_json", postgresql.JSONB(), nullable=True),
        sa.Column("contact_type", sa.String(16), nullable=True),
        sa.Column("contact_value", sa.String(255), nullable=True),
        sa.Column("source_last_modified", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("check_state", sa.String(20), nullable=False, server_default="ok"),
        sa.Column("deleted_at_source", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_listings_filter", "listings", ["status", "intent", "area", "has_room"])
    op.create_index("ix_listings_published_at", "listings", ["published_at"])
    op.create_index("ix_listings_budget", "listings", ["budget_min", "budget_max"])

    op.create_table(
        "favorites",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "listing_id",
            sa.Integer(),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("personal_status", sa.String(16), nullable=False, server_default="saved"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("favorites")
    op.drop_index("ix_listings_budget", table_name="listings")
    op.drop_index("ix_listings_published_at", table_name="listings")
    op.drop_index("ix_listings_filter", table_name="listings")
    op.drop_table("listings")
    op.drop_table("users")
