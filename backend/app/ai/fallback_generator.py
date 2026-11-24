"""Algorithmic deterministic fallback generator ensuring 100% application resilience."""

from app.ai.schemas import (
    ActionRecommendationItem,
    BreatheSmartActionPlanResponse,
    ConfidenceLevel,
    ImpactType,
    RecommendationCategory,
    RecommendationPriority,
    RiskLevel,
)
from app.schemas.air_quality import NormalizedAirQuality


class DeterministicFallbackGenerator:
    """Generates structured, validated action plans if the Groq GenAI service is unavailable."""

    @classmethod
    def generate_plan(
        cls,
        aqi_data: NormalizedAirQuality,
        user_prefs: dict | None = None,
    ) -> BreatheSmartActionPlanResponse:
        aqi = aqi_data.aqi
        pm25 = aqi_data.pollutants.pm2_5.value if aqi_data.pollutants.pm2_5 else 0.0

        if aqi <= 50:
            risk = RiskLevel.GOOD
            summary = "Air quality is good. It is ideal for all outdoor activities and natural home ventilation."
            explanation = f"PM2.5 concentration is low ({pm25:.1f} µg/m³). Clean air allows full natural ventilation."
        elif aqi <= 100:
            risk = RiskLevel.MODERATE
            summary = "Air quality is acceptable. Sensitive individuals should observe minor precautions."
            explanation = f"PM2.5 concentration is moderate ({pm25:.1f} µg/m³). Outdoor exercise is generally safe."
        elif aqi <= 200:
            risk = RiskLevel.HIGH
            summary = "Elevated particulate pollution detected. Modify outdoor routines and limit ventilation."
            explanation = f"Elevated PM2.5 levels ({pm25:.1f} µg/m³). Smog accumulation reduces safe outdoor windows."
        else:
            risk = RiskLevel.SEVERE
            summary = "Severe smog and hazardous particulate levels. Prioritize indoor protection and minimize outdoor exposure."
            explanation = f"Dangerous PM2.5 levels ({pm25:.1f} µg/m³). Particulate infiltration poses serious exposure risks."

        recommendations = [
            ActionRecommendationItem(
                title="Morning Routine & Exercise Adjustment",
                category=RecommendationCategory.OUTDOOR,
                priority=RecommendationPriority.URGENT if aqi > 150 else RecommendationPriority.MEDIUM,
                recommended_time="06:00 - 09:00 AM",
                action=(
                    "Shift strenuous cardio indoors; avoid running near high-traffic corridors."
                    if aqi > 100
                    else "Safe for outdoor exercise and walking."
                ),
                reason="Morning temperature inversions trap surface particulates at ground level.",
                expected_impact="Reduces acute particulate lung deposition by 40-70%.",
                impact_type=ImpactType.EXPOSURE,
                confidence=ConfidenceLevel.HIGH,
                assumptions=["Assumes ground-level temperature inversion during winter early mornings."],
            ),
            ActionRecommendationItem(
                title="Controlled Home Ventilation Window",
                category=RecommendationCategory.INDOOR,
                priority=RecommendationPriority.HIGH,
                recommended_time="01:00 - 02:30 PM",
                action=(
                    "Open cross-ventilating windows for 20-30 minutes during afternoon solar peak, then reseal and engage purifier."
                    if aqi > 150
                    else "Open windows freely for natural ventilation."
                ),
                reason="Midday solar warming lifts the atmospheric inversion layer, reducing surface pollution.",
                expected_impact="Purges indoor CO2 and moisture buildup while minimizing particulate ingress.",
                impact_type=ImpactType.EXPOSURE,
                confidence=ConfidenceLevel.HIGH,
                assumptions=["Assumes afternoon boundary layer rise allows lower ground concentrations."],
            ),
            ActionRecommendationItem(
                title="Low-Emission Commute Mode Choice",
                category=RecommendationCategory.COMMUTE,
                priority=RecommendationPriority.MEDIUM,
                recommended_time="Daily Commute",
                action="Opt for electrified metro or bus transit rather than single-occupancy petrol vehicles.",
                reason="Public transit reduces per-capita combustion emissions along congested corridors.",
                expected_impact="Eliminates ~2.4 kg CO2e per 15 km trip and reduces personal cabin pollution exposure.",
                impact_type=ImpactType.EMISSIONS,
                confidence=ConfidenceLevel.HIGH,
                assumptions=["Calculated based on standard DEFRA passenger transit emission factors."],
            ),
            ActionRecommendationItem(
                title="Nighttime Indoor Air Quality Protection",
                category=RecommendationCategory.INDOOR,
                priority=RecommendationPriority.HIGH if aqi > 150 else RecommendationPriority.LOW,
                recommended_time="10:00 PM - 06:00 AM",
                action="Run HEPA air purifier on quiet/sleep mode in bedrooms; ensure cooking exhaust is off and doors closed.",
                reason="Continuous filtration maintains low PM2.5 levels throughout the 8-hour sleep cycle.",
                expected_impact="Maintains indoor PM2.5 below 15 µg/m³ during sleep.",
                impact_type=ImpactType.EXPOSURE,
                confidence=ConfidenceLevel.HIGH,
                assumptions=["Assumes standard CADR rating matching bedroom volume."],
            ),
        ]

        return BreatheSmartActionPlanResponse(
            summary=summary,
            risk_level=risk,
            explanation=explanation,
            recommendations=recommendations,
            limitations=[
                "Generated via deterministic rule engine as resilient fallback.",
                f"Based on {aqi_data.source_metadata.provider} {aqi_data.source_metadata.data_type.value} data.",
            ],
            safety_notes=[
                "General environmental wellness guidance only; not medical advice.",
                "Individuals with pre-existing cardiopulmonary conditions should consult healthcare providers.",
            ],
        )
