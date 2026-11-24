import uuid

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    recommendation_id: uuid.UUID
    rating: int = Field(ge=1, le=5, description="Rating from 1 (poor) to 5 (excellent)")
    feedback: str | None = Field(default=None, max_length=1000)


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    recommendation_id: uuid.UUID
    rating: int
    feedback: str | None

    class Config:
        from_attributes = True
