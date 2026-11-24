"""RecommendationPlan model for persisted AI action plans."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.feedback import UserFeedback
    from app.models.session import UserSession


class RecommendationPlan(Base):
    __tablename__ = "recommendation_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("saved_locations.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("air_quality_snapshots.id", ondelete="SET NULL"),
        nullable=True,
    )
    ai_model: Mapped[str] = mapped_column(
        String(50),
        default="openai/gpt-oss-120b",
        nullable=False,
    )
    recommendation_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    session: Mapped["UserSession"] = relationship(
        "UserSession",
        back_populates="recommendations",
    )
    feedbacks: Mapped[list["UserFeedback"]] = relationship(
        "UserFeedback",
        back_populates="recommendation",
        cascade="all, delete-orphan",
    )
