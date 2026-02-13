"""SQLAlchemy ORM models - shared between API and Processor."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Text, VARCHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.common.database import Base


class Content(Base):
    """Content submission model."""

    __tablename__ = "content"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    moderation_result: Mapped[Optional["ModerationResult"]] = relationship(
        "ModerationResult", back_populates="content", uselist=False
    )


class ModerationResult(Base):
    """Moderation result model."""

    __tablename__ = "moderation_results"

    content_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content.id", ondelete="CASCADE"),
        primary_key=True,
    )
    status: Mapped[str] = mapped_column(VARCHAR(50), nullable=False, default="PENDING")
    moderated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    content: Mapped["Content"] = relationship(
        "Content", back_populates="moderation_result"
    )
