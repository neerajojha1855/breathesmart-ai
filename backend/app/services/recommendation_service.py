"""Recommendation Service: Orchestrates environmental intelligence, AI synthesis, and domain calculators."""

import logging
from typing import Any
from app.ai.groq_client import GroqAIService
from app.ai.schemas import BreatheSmartActionPlanResponse
from app.providers.air_quality.open_meteo import OpenMeteoAirQualityProvider
from app.schemas.air_quality import AirQualityForecast, NormalizedAirQuality
from app.services.indoor_air_service import IndoorAirAdvisorReport, IndoorAirService
from app.services.sustainability_service import CommuteShiftImpact, SustainabilityService, TransportMode

logger = logging.getLogger(__name__)


class RecommendationService:
    """Central orchestrator for BreatheSmart AI daily planning and environmental advisory."""

    def __init__(
        self,
        aq_provider: OpenMeteoAirQualityProvider | None = None,
        ai_service: GroqAIService | None = None,
    ) -> None:
        self.aq_provider = aq_provider or OpenMeteoAirQualityProvider()
        self.ai_service = ai_service or GroqAIService()

    async def get_daily_action_plan(
        self,
        latitude: float,
        longitude: float,
        user_preferences: dict[str, Any] | None = None,
    ) -> BreatheSmartActionPlanResponse:
        """Fetch live air quality data and generate a personalized 4-segment daily action plan."""
        # 1. Fetch live normalized air quality
        aqi_data = await self.aq_provider.get_current_air_quality(latitude, longitude)

        # 2. Generate personalized action plan using Groq (or fallback)
        plan = await self.ai_service.generate_action_plan(aqi_data, user_preferences)
        return plan

    async def get_indoor_advisor_report(
        self,
        latitude: float,
        longitude: float,
        has_purifier: bool = True,
    ) -> IndoorAirAdvisorReport:
        """Generate scientific indoor air quality guidance balancing ventilation and filtration."""
        aqi_data = await self.aq_provider.get_current_air_quality(latitude, longitude)
        forecast = await self.aq_provider.get_forecast(latitude, longitude, forecast_days=2)
        return IndoorAirService.generate_full_advisor_report(aqi_data, has_purifier=has_purifier, forecast=forecast)

    def calculate_sustainability_impact(
        self,
        baseline_mode: TransportMode,
        alternative_mode: TransportMode,
        distance_km: float,
        trips_per_week: int = 10,
    ) -> CommuteShiftImpact:
        """Calculate quantified emission reductions and exposure avoidance for transport shifts."""
        return SustainabilityService.calculate_commute_shift(
            baseline_mode=baseline_mode,
            alternative_mode=alternative_mode,
            distance_km=distance_km,
            trips_per_week=trips_per_week,
        )
