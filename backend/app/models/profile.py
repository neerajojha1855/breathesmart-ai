"""UserProfile model with JSONB preferences."""

import uuid
from typing import TYPE_CHECKING, Any
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.session import UserSession


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_sessions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    preferred_language: Mapped[str] = mapped_column(
        String(10),
        default="en",
        nullable=False,
    )
    household_preferences: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )
    commuting_preferences: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )
    indoor_environment_preferences: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )
    sensitive_group_consent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    session: Mapped["UserSession"] = relationship(
        "UserSession",
        back_populates="profile",
    )
