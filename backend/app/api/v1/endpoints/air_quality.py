from fastapi import APIRouter, Query
from app.providers.air_quality.open_meteo import OpenMeteoAirQualityProvider
from app.schemas.air_quality import AirQualityForecast, NormalizedAirQuality

router = APIRouter(prefix="/air-quality", tags=["Air Quality"])
aq_provider = OpenMeteoAirQualityProvider()


@router.get("/current", response_model=NormalizedAirQuality)
async def get_current_air_quality(
    latitude: float = Query(ge=-90.0, le=90.0),
    longitude: float = Query(ge=-180.0, le=180.0),
):
    """Fetch live normalized air quality readings, AQI classification, and pollutant breakdown."""
    return await aq_provider.get_current_air_quality(latitude, longitude)


@router.get("/forecast", response_model=AirQualityForecast)
async def get_air_quality_forecast(
    latitude: float = Query(ge=-90.0, le=90.0),
    longitude: float = Query(ge=-180.0, le=180.0),
    days: int = Query(default=5, ge=1, le=7),
):
    """Fetch hourly air quality forecast points across next 1 to 7 days."""
    return await aq_provider.get_forecast(latitude, longitude, forecast_days=days)
