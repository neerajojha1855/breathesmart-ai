"""Pydantic schemas for normalized air quality and atmospheric data."""

from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class AQICategory(str, Enum):
    GOOD = "good"
    MODERATE = "moderate"
    UNHEALTHY_SENSITIVE = "unhealthy_for_sensitive_groups"
    UNHEALTHY = "unhealthy"
    VERY_UNHEALTHY = "very_unhealthy"
    HAZARDOUS = "hazardous"
    UNKNOWN = "unknown"


class AQIStandard(str, Enum):
    US_AQI = "US_AQI"
    EU_AQI = "EU_AQI"
    CPCB = "CPCB"


class DataSourceType(str, Enum):
    MEASURED = "measured"
    MODELED = "modeled"
    FORECAST = "forecast"


class PollutantMeasurement(BaseModel):
    value: float
    unit: str = "µg/m³"
    category: AQICategory = AQICategory.UNKNOWN


class Pollutants(BaseModel):
    pm2_5: PollutantMeasurement | None = None
    pm10: PollutantMeasurement | None = None
    no2: PollutantMeasurement | None = None
    so2: PollutantMeasurement | None = None
    o3: PollutantMeasurement | None = None
    co: PollutantMeasurement | None = None


class SourceMetadata(BaseModel):
    provider: str = "Open-Meteo"
    data_type: DataSourceType = DataSourceType.MODELED
    source_resolution: str = "11km atmospheric CAMS grid"
    observed_at: datetime
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    freshness_seconds: int = 0
    license_attribution: str = "Contains Copernicus Atmosphere Monitoring Service Information"


class NormalizedAirQuality(BaseModel):
    latitude: float
    longitude: float
    timezone: str = "UTC"
    aqi: int
    aqi_standard: AQIStandard = AQIStandard.US_AQI
    aqi_category: AQICategory
    dominant_pollutant: str = "pm2_5"
    pollutants: Pollutants
    source_metadata: SourceMetadata


class HourlyForecastPoint(BaseModel):
    timestamp: datetime
    aqi: int
    aqi_category: AQICategory
    pm2_5: float
    pm10: float
    no2: float | None = None
    o3: float | None = None


class AirQualityForecast(BaseModel):
    latitude: float
    longitude: float
    aqi_standard: AQIStandard = AQIStandard.US_AQI
    hourly: list[HourlyForecastPoint]
    source_metadata: SourceMetadata
