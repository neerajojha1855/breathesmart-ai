"""Unit tests verifying AQI normalization, schema parsing, and caching."""

import pytest
from app.providers.air_quality.open_meteo import OpenMeteoAirQualityProvider, calculate_us_aqi_category
from app.schemas.air_quality import AQICategory, AQIStandard, DataSourceType


def test_aqi_category_calculation():
    assert calculate_us_aqi_category(25) == AQICategory.GOOD
    assert calculate_us_aqi_category(75) == AQICategory.MODERATE
    assert calculate_us_aqi_category(125) == AQICategory.UNHEALTHY_SENSITIVE
    assert calculate_us_aqi_category(175) == AQICategory.UNHEALTHY
    assert calculate_us_aqi_category(250) == AQICategory.VERY_UNHEALTHY
    assert calculate_us_aqi_category(350) == AQICategory.HAZARDOUS


@pytest.mark.asyncio
async def test_open_meteo_live_data_normalization():
    # Test coordinates for New Delhi (28.6139, 77.2090)
    provider = OpenMeteoAirQualityProvider()
    data = await provider.get_current_air_quality(28.6139, 77.2090)

    assert data.latitude is not None
    assert data.longitude is not None
    assert data.aqi_standard == AQIStandard.US_AQI
    assert data.source_metadata.provider == "Open-Meteo"
    assert data.source_metadata.data_type == DataSourceType.MODELED
    assert data.pollutants.pm2_5 is not None
    assert data.pollutants.pm2_5.unit == "µg/m³"

    # Verify in-memory caching: same object returned within TTL
    cached_data = await provider.get_current_air_quality(28.6139, 77.2090)
    assert cached_data is data


@pytest.mark.asyncio
async def test_open_meteo_forecast():
    provider = OpenMeteoAirQualityProvider()
    forecast = await provider.get_forecast(28.6139, 77.2090, forecast_days=2)

    assert forecast.hourly is not None
    assert len(forecast.hourly) > 0
    first_pt = forecast.hourly[0]
    assert first_pt.aqi >= 0
    assert first_pt.pm2_5 >= 0.0
