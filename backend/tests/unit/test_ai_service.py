"""Unit tests verifying Groq AI integration, schema validation, and fallback resilience."""

from datetime import UTC, datetime

import pytest
from app.ai.fallback_generator import DeterministicFallbackGenerator
from app.ai.groq_client import GroqAIService
from app.ai.schemas import (
    AIChatRequest,
    BreatheSmartActionPlanResponse,
    RecommendationCategory,
    RiskLevel,
)
from app.schemas.air_quality import (
    AQICategory,
    AQIStandard,
    DataSourceType,
    NormalizedAirQuality,
    PollutantMeasurement,
    Pollutants,
    SourceMetadata,
)


@pytest.fixture
def mock_aqi_data() -> NormalizedAirQuality:
    return NormalizedAirQuality(
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
        aqi=240,
        aqi_standard=AQIStandard.US_AQI,
        aqi_category=AQICategory.VERY_UNHEALTHY,
        dominant_pollutant="pm2_5",
        pollutants=Pollutants(
            pm2_5=PollutantMeasurement(value=190.0, unit="µg/m³"),
            pm10=PollutantMeasurement(value=310.0, unit="µg/m³"),
        ),
        source_metadata=SourceMetadata(
            provider="Open-Meteo",
            data_type=DataSourceType.MODELED,
            observed_at=datetime.now(UTC),
        ),
    )


def test_fallback_generator_schema_compliance(mock_aqi_data: NormalizedAirQuality):
    plan = DeterministicFallbackGenerator.generate_plan(mock_aqi_data)
    assert isinstance(plan, BreatheSmartActionPlanResponse)
    assert plan.risk_level == RiskLevel.SEVERE
    assert len(plan.recommendations) >= 4

    categories = [rec.category for rec in plan.recommendations]
    assert RecommendationCategory.OUTDOOR in categories
    assert RecommendationCategory.INDOOR in categories
    assert RecommendationCategory.COMMUTE in categories


@pytest.mark.asyncio
async def test_groq_service_live_or_fallback(mock_aqi_data: NormalizedAirQuality):
    service = GroqAIService()
    plan = await service.generate_action_plan(mock_aqi_data)
    assert isinstance(plan, BreatheSmartActionPlanResponse)
    assert plan.summary is not None
    assert len(plan.recommendations) > 0


@pytest.mark.asyncio
async def test_chat_assistant_response(mock_aqi_data: NormalizedAirQuality):
    service = GroqAIService()
    req = AIChatRequest(message="Is it safe for my child to run outdoors this morning?")
    resp = await service.chat_assistant(req, mock_aqi_data)
    assert resp.message is not None
    assert len(resp.message) > 10
    assert len(resp.suggested_followups) >= 1
