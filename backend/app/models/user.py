from datetime import UTC, datetime

from sqlalchemy import DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("provider", "provider_id", name="uq_user_provider"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(16))  # 'google' | 'wechat'
    provider_id: Mapped[str] = mapped_column(String(128))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    role: Mapped[str] = mapped_column(String(16), default="user")  # 'user' | 'admin'
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
