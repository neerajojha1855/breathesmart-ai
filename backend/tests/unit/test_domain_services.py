"""Unit tests for sustainability emissions calculator, indoor air service, and recommendation orchestrator."""

from datetime import datetime, timezone
import pytest
from app.schemas.air_quality import (
    AQICategory,
    AQIStandard,
    DataSourceType,
    NormalizedAirQuality,
    PollutantMeasurement,
    Pollutants,
    SourceMetadata,
)
from app.services.indoor_air_service import IndoorAirService, VentilationSuitability
from app.services.recommendation_service import RecommendationService
from app.services.sustainability_service import SustainabilityService, TransportMode


@pytest.fixture
def clean_aqi_data() -> NormalizedAirQuality:
    return NormalizedAirQuality(
        latitude=28.6139,
        longitude=77.2090,
        timezone="UTC",
        aqi=35,
        aqi_standard=AQIStandard.US_AQI,
        aqi_category=AQICategory.GOOD,
        dominant_pollutant="pm2_5",
        pollutants=Pollutants(
            pm2_5=PollutantMeasurement(value=8.5, unit="µg/m³"),
            pm10=PollutantMeasurement(value=18.0, unit="µg/m³"),
        ),
        source_metadata=SourceMetadata(
            provider="Open-Meteo",
            data_type=DataSourceType.MODELED,
            observed_at=datetime.now(timezone.utc),
        ),
    )


@pytest.fixture
def smog_aqi_data() -> NormalizedAirQuality:
    return NormalizedAirQuality(
        latitude=28.6139,
        longitude=77.2090,
        timezone="UTC",
        aqi=260,
        aqi_standard=AQIStandard.US_AQI,
        aqi_category=AQICategory.VERY_UNHEALTHY,
        dominant_pollutant="pm2_5",
        pollutants=Pollutants(
            pm2_5=PollutantMeasurement(value=210.0, unit="µg/m³"),
            pm10=PollutantMeasurement(value=350.0, unit="µg/m³"),
        ),
        source_metadata=SourceMetadata(
            provider="Open-Meteo",
            data_type=DataSourceType.MODELED,
            observed_at=datetime.now(timezone.utc),
        ),
    )


def test_sustainability_commute_shift_calculation():
    # Shifting 15 km daily commute from Petrol Car to Metro Train
    impact = SustainabilityService.calculate_commute_shift(
        baseline_mode=TransportMode.PETROL_CAR,
        alternative_mode=TransportMode.METRO_TRAIN,
        distance_km=15.0,
        trips_per_week=10,
    )

    # 15 km * (0.171 - 0.028) = 15 * 0.143 = 2.145 kg per trip
    # 2.145 * 10 = 21.45 kg per week
    assert impact.weekly_co2e_saved_kg > 20.0
    assert impact.annual_co2e_saved_kg > 1000.0
    assert impact.trees_equivalent_annual > 40.0
    assert "Subway / underground trains" in impact.particulate_exposure_benefit
    assert len(impact.assumptions) >= 4


def test_indoor_air_ventilation_safety_clean_vs_smog(
    clean_aqi_data: NormalizedAirQuality,
    smog_aqi_data: NormalizedAirQuality,
):
    # Under clean air: optimal ventilation
    clean_rec = IndoorAirService.evaluate_ventilation(clean_aqi_data)
    assert clean_rec.suitability == VentilationSuitability.OPTIMAL
    assert clean_rec.can_open_windows is True

    # Under severe smog: hazardous ventilation, keep sealed
    smog_rec = IndoorAirService.evaluate_ventilation(smog_aqi_data)
    assert smog_rec.suitability == VentilationSuitability.HAZARDOUS
    assert smog_rec.can_open_windows is False
    assert smog_rec.max_duration_minutes == 0


def test_indoor_advisor_report_generation(smog_aqi_data: NormalizedAirQuality):
    report = IndoorAirService.generate_full_advisor_report(smog_aqi_data, has_purifier=True)
    assert report.ventilation.can_open_windows is False
    assert "Turbo" in report.purification.recommended_mode
    assert len(report.cooking_safety_checklist) >= 3
    assert len(report.combustion_hazards_to_avoid) >= 3


@pytest.mark.asyncio
async def test_recommendation_service_orchestration():
    service = RecommendationService()
    # Test for coordinates of New Delhi
    plan = await service.get_daily_action_plan(28.6139, 77.2090)
    assert plan.summary is not None
    assert len(plan.recommendations) > 0

    advisor = await service.get_indoor_advisor_report(28.6139, 77.2090)
    assert advisor.ventilation is not None
    assert advisor.purification is not None
