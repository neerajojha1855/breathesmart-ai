from pydantic import BaseModel, Field

from app.services.sustainability_service import TransportMode


class CommuteShiftRequest(BaseModel):
    baseline_mode: TransportMode
    alternative_mode: TransportMode
    distance_km: float = Field(
        gt=0, description="One-way commute distance in kilometers"
    )
    trips_per_week: int = Field(default=10, ge=1, le=28)
