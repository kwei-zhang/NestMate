from datetime import UTC, date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

# JSONB on Postgres, plain JSON elsewhere (e.g. SQLite in tests).
JSONType = JSON().with_variant(JSONB(), "postgresql")

# Enumerated string values (kept as plain strings for simplicity/portability)
SOURCE_VALUES = ("xhs", "native")
STATUS_VALUES = ("pending_review", "published", "archived")
INTENT_VALUES = ("offering", "seeking")  # offering=招租(有房源) / seeking=求租
CONTACT_TYPES = ("wechat", "phone", "xhs", "email")
CHECK_STATES = ("ok", "changed_needs_ai", "auto_archived")


class Listing(Base):
    __tablename__ = "listings"
    __table_args__ = (
        Index("ix_listings_filter", "status", "intent", "area", "has_room"),
        Index("ix_listings_published_at", "published_at"),
        Index("ix_listings_budget", "budget_min", "budget_max"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(16))  # xhs | native
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending_review")

    # AI-extracted, filterable columns
    intent: Mapped[str | None] = mapped_column(String(16), nullable=True)
    has_room: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    mbti: Mapped[str | None] = mapped_column(String(8), nullable=True)
    has_pets: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    pets_note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    budget_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    budget_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    area: Mapped[str | None] = mapped_column(String(128), nullable=True)
    move_in_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender_pref: Mapped[str | None] = mapped_column(String(32), nullable=True)
    extracted_json: Mapped[dict | None] = mapped_column(JSONType, nullable=True)

    # Contact (gated — never returned in public payloads)
    contact_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    contact_value: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Staleness tracking
    source_last_modified: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    check_state: Mapped[str] = mapped_column(String(20), default="ok")
    deleted_at_source: Mapped[bool] = mapped_column(Boolean, default=False)

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
