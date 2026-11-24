import uuid
from typing import Annotated

from app.api.deps import get_db, get_or_create_session
from app.models.feedback import UserFeedback
from app.models.session import UserSession
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    fb_in: FeedbackCreate,
    session: Annotated[UserSession, Depends(get_or_create_session)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Submit rating and feedback for a generated recommendation plan."""
    new_fb = UserFeedback(
        id=uuid.uuid4(),
        session_id=session.id,
        recommendation_id=fb_in.recommendation_id,
        rating=fb_in.rating,
        feedback=fb_in.feedback,
    )
    db.add(new_fb)
    await db.commit()
    await db.refresh(new_fb)
    return new_fb
