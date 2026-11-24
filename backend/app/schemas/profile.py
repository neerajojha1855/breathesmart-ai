import uuid
from typing import Any

from pydantic import BaseModel, Field


class UserProfileUpdate(BaseModel):
    preferred_language: str = "en"
    household_preferences: dict[str, Any] = Field(default_factory=dict)
    commuting_preferences: dict[str, Any] = Field(default_factory=dict)
    indoor_environment_preferences: dict[str, Any] = Field(default_factory=dict)
    sensitive_group_consent: bool = False


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    preferred_language: str
    household_preferences: dict[str, Any]
    commuting_preferences: dict[str, Any]
    indoor_environment_preferences: dict[str, Any]
    sensitive_group_consent: bool

    class Config:
        from_attributes = True
