from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_or_create_session
from app.models.profile import UserProfile
from app.models.session import UserSession
from app.schemas.profile import UserProfileResponse, UserProfileUpdate

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=UserProfileResponse)
async def get_profile(
    session: Annotated[UserSession, Depends(get_or_create_session)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Fetch current user session profile."""
    stmt = select(UserProfile).where(UserProfile.session_id == session.id)
    res = await db.execute(stmt)
    return res.scalar_one()


@router.put("", response_model=UserProfileResponse)
async def update_profile(
    update_data: UserProfileUpdate,
    session: Annotated[UserSession, Depends(get_or_create_session)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update user preferences for personalized recommendations."""
    stmt = select(UserProfile).where(UserProfile.session_id == session.id)
    res = await db.execute(stmt)
    profile = res.scalar_one()

    profile.preferred_language = update_data.preferred_language
    profile.household_preferences = update_data.household_preferences
    profile.commuting_preferences = update_data.commuting_preferences
    profile.indoor_environment_preferences = update_data.indoor_environment_preferences
    profile.sensitive_group_consent = update_data.sensitive_group_consent

    await db.commit()
    await db.refresh(profile)
    return profile
