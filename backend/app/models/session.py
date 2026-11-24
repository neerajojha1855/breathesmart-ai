"""UserSession model storing cryptographic session token hashes."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.feedback import UserFeedback
    from app.models.location import SavedLocation
    from app.models.profile import UserProfile
    from app.models.recommendation import RecommendationPlan


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    profile: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    locations: Mapped[list["SavedLocation"]] = relationship(
        "SavedLocation",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    recommendations: Mapped[list["RecommendationPlan"]] = relationship(
        "RecommendationPlan",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    feedbacks: Mapped[list["UserFeedback"]] = relationship(
        "UserFeedback",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
