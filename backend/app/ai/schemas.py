"""Pydantic schemas for structured Groq GenAI responses and conversational assistant."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class RecommendationCategory(StrEnum):
    OUTDOOR = "outdoor"
    INDOOR = "indoor"
    COMMUTE = "commute"
    SUSTAINABILITY = "sustainability"


class RecommendationPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ImpactType(StrEnum):
    EXPOSURE = "exposure"
    EMISSIONS = "emissions"
    ENERGY = "energy"
    QUALITATIVE = "qualitative"


class ConfidenceLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskLevel(StrEnum):
    GOOD = "good"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    UNKNOWN = "unknown"


class ActionRecommendationItem(BaseModel):
    title: str = Field(description="Short, action-oriented title")
    category: RecommendationCategory
    priority: RecommendationPriority
    recommended_time: str = Field(
        description="Time window e.g., '06:00 - 08:00 AM' or 'Evening'"
    )
    action: str = Field(description="Specific, practical step to carry out")
    reason: str = Field(description="Underlying atmospheric or behavioral rationale")
    expected_impact: str = Field(description="Expected benefit description")
    impact_type: ImpactType
    confidence: ConfidenceLevel
    assumptions: list[str] = Field(
        default_factory=list, description="Explicit assumptions or limitations"
    )


class BreatheSmartActionPlanResponse(BaseModel):
    summary: str = Field(
        description="Executive summary of today's environmental situation"
    )
    risk_level: RiskLevel
    explanation: str = Field(
        description="Accessible explanation of primary pollutants without medical advice"
    )
    recommendations: list[ActionRecommendationItem]
    limitations: list[str] = Field(
        default_factory=list, description="Data boundaries or modeling assumptions"
    )
    safety_notes: list[str] = Field(
        default_factory=list, description="General health precautions"
    )


class AIChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str


class AIChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    history: list[AIChatMessage] = Field(default_factory=list, max_length=10)
    user_context: dict[str, Any] = Field(default_factory=dict)


class AIChatResponse(BaseModel):
    message: str
    suggested_followups: list[str] = Field(default_factory=list)
    context_sources: list[str] = Field(default_factory=list)
    disclaimer: str = (
        "General environmental wellness information only; not formal medical advice."
    )
