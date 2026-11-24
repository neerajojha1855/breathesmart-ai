from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.ai.schemas import BreatheSmartActionPlanResponse
from app.api.deps import get_or_create_session
from app.models.session import UserSession
from app.services.indoor_air_service import IndoorAirAdvisorReport
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])
service = RecommendationService()


@router.post("/generate", response_model=BreatheSmartActionPlanResponse)
async def generate_action_plan(
    latitude: float = Query(ge=-90.0, le=90.0),
    longitude: float = Query(ge=-180.0, le=180.0),
    session: Annotated[UserSession | None, Depends(get_or_create_session)] = None,
):
    """Generate a personalized daily action plan with morning, afternoon, evening, and night recommendations."""
    prefs = session.profile.household_preferences if session and session.profile else {}
    return await service.get_daily_action_plan(
        latitude, longitude, user_preferences=prefs
    )


@router.get("/indoor", response_model=IndoorAirAdvisorReport)
async def get_indoor_advisor(
    latitude: float = Query(ge=-90.0, le=90.0),
    longitude: float = Query(ge=-180.0, le=180.0),
    has_purifier: bool = Query(default=True),
):
    """Scientific indoor ventilation and HEPA purification advisor."""
    return await service.get_indoor_advisor_report(
        latitude, longitude, has_purifier=has_purifier
    )
