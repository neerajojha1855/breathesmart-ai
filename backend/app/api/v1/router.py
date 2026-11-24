"""Master v1 API Router combining all sub-routers."""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    air_quality,
    assistant,
    feedback,
    locations,
    profile,
    recommendations,
    sustainability,
)

api_router = APIRouter()
api_router.include_router(locations.router)
api_router.include_router(air_quality.router)
api_router.include_router(recommendations.router)
api_router.include_router(sustainability.router)
api_router.include_router(assistant.router)
api_router.include_router(profile.router)
api_router.include_router(feedback.router)
