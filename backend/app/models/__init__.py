"""Expose all SQLAlchemy models for Alembic discovery."""

from app.models.air_quality import AirQualitySnapshot
from app.models.base import Base
from app.models.feedback import UserFeedback
from app.models.location import SavedLocation
from app.models.profile import UserProfile
from app.models.recommendation import RecommendationPlan
from app.models.session import UserSession

__all__ = [
    "AirQualitySnapshot",
    "Base",
    "RecommendationPlan",
    "SavedLocation",
    "UserFeedback",
    "UserProfile",
    "UserSession",
]
