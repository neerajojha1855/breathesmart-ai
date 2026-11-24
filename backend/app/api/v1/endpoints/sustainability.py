from fastapi import APIRouter

from app.schemas.sustainability import CommuteShiftRequest
from app.services.sustainability_service import (
    CommuteShiftImpact,
    SustainabilityService,
)

router = APIRouter(prefix="/sustainability", tags=["Sustainability"])


@router.post("/compare", response_model=CommuteShiftImpact)
async def compare_commute_modes(req: CommuteShiftRequest):
    """Calculate quantified emission reductions and acute personal particulate exposure benefits."""
    return SustainabilityService.calculate_commute_shift(
        baseline_mode=req.baseline_mode,
        alternative_mode=req.alternative_mode,
        distance_km=req.distance_km,
        trips_per_week=req.trips_per_week,
    )
