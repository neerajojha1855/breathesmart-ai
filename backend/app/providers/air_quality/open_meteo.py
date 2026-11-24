"""Open-Meteo Air Quality provider implementation with caching and resilient retries."""

import asyncio
import random
import time
from datetime import UTC, datetime
from typing import Any

import httpx
from app.core.exceptions import AirQualityProviderError
from app.providers.air_quality.base import BaseAirQualityProvider
from app.schemas.air_quality import (
    AirQualityForecast,
    AQICategory,
    AQIStandard,
    DataSourceType,
    HourlyForecastPoint,
    NormalizedAirQuality,
    PollutantMeasurement,
    Pollutants,
    SourceMetadata,
)


def calculate_us_aqi_category(aqi_val: int) -> AQICategory:
    if aqi_val <= 50:
        return AQICategory.GOOD
    elif aqi_val <= 100:
        return AQICategory.MODERATE
    elif aqi_val <= 150:
        return AQICategory.UNHEALTHY_SENSITIVE
    elif aqi_val <= 200:
        return AQICategory.UNHEALTHY
    elif aqi_val <= 300:
        return AQICategory.VERY_UNHEALTHY
    return AQICategory.HAZARDOUS


class OpenMeteoAirQualityProvider(BaseAirQualityProvider):
    BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
    CACHE_TTL_SECONDS = 900  # 15 minutes

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(timeout=10.0)
        self._cache: dict[str, tuple[float, Any]] = {}

    async def aclose(self) -> None:
        if not self._client.is_closed:
            await self._client.aclose()

    def _cache_key(self, prefix: str, lat: float, lon: float) -> str:
        return f"{prefix}:{round(lat, 3)}:{round(lon, 3)}"

    async def _fetch_with_retry(self, params: dict[str, Any]) -> dict[str, Any]:
        max_retries = 3
        backoff = 0.5
        for attempt in range(max_retries):
            try:
                response = await self._client.get(self.BASE_URL, params=params)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    jitter = random.uniform(0.1, 0.3)
                    await asyncio.sleep(backoff + jitter)
                    backoff *= 2
                    continue
                else:
                    raise AirQualityProviderError(
                        f"Open-Meteo responded with status {response.status_code}",
                        {
                            "status_code": response.status_code,
                            "body": response.text[:200],
                        },
                    )
            except httpx.RequestError as exc:
                if attempt == max_retries - 1:
                    raise AirQualityProviderError(
                        f"Network error contacting Open-Meteo: {exc}"
                    ) from exc
                await asyncio.sleep(backoff + random.uniform(0.1, 0.2))
                backoff *= 2
        raise AirQualityProviderError("Max retries exceeded contacting Open-Meteo")

    async def get_current_air_quality(
        self, latitude: float, longitude: float
    ) -> NormalizedAirQuality:
        key = self._cache_key("current", latitude, longitude)
        now = time.time()
        if key in self._cache and (now - self._cache[key][0]) < self.CACHE_TTL_SECONDS:
            return self._cache[key][1]

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "us_aqi",
                "pm2_5",
                "pm10",
                "nitrogen_dioxide",
                "sulphur_dioxide",
                "ozone",
                "carbon_monoxide",
            ],
            "timezone": "auto",
        }
        data = await self._fetch_with_retry(params)
        curr = data.get("current", {})

        us_aqi = int(curr.get("us_aqi") or 0)
        aqi_cat = calculate_us_aqi_category(us_aqi)

        pollutants = Pollutants(
            pm2_5=PollutantMeasurement(
                value=float(curr.get("pm2_5") or 0.0), unit="µg/m³"
            ),
            pm10=PollutantMeasurement(
                value=float(curr.get("pm10") or 0.0), unit="µg/m³"
            ),
            no2=PollutantMeasurement(
                value=float(curr.get("nitrogen_dioxide") or 0.0), unit="µg/m³"
            ),
            so2=PollutantMeasurement(
                value=float(curr.get("sulphur_dioxide") or 0.0), unit="µg/m³"
            ),
            o3=PollutantMeasurement(
                value=float(curr.get("ozone") or 0.0), unit="µg/m³"
            ),
            co=PollutantMeasurement(
                value=float(curr.get("carbon_monoxide") or 0.0), unit="µg/m³"
            ),
        )

        obs_time_str = curr.get("time")
        obs_time = (
            datetime.fromisoformat(obs_time_str) if obs_time_str else datetime.now(UTC)
        )

        result = NormalizedAirQuality(
            latitude=data.get("latitude", latitude),
            longitude=data.get("longitude", longitude),
            timezone=data.get("timezone", "UTC"),
            aqi=us_aqi,
            aqi_standard=AQIStandard.US_AQI,
            aqi_category=aqi_cat,
            dominant_pollutant="pm2_5",
            pollutants=pollutants,
            source_metadata=SourceMetadata(
                provider="Open-Meteo",
                data_type=DataSourceType.MODELED,
                source_resolution="11km atmospheric CAMS grid",
                observed_at=obs_time,
                freshness_seconds=max(0, int(now - obs_time.timestamp()))
                if obs_time.tzinfo
                else 0,
            ),
        )
        self._cache[key] = (now, result)
        return result

    async def get_forecast(
        self, latitude: float, longitude: float, forecast_days: int = 5
    ) -> AirQualityForecast:
        key = self._cache_key(f"forecast_{forecast_days}", latitude, longitude)
        now = time.time()
        if key in self._cache and (now - self._cache[key][0]) < self.CACHE_TTL_SECONDS:
            return self._cache[key][1]

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ["us_aqi", "pm2_5", "pm10", "nitrogen_dioxide", "ozone"],
            "forecast_days": forecast_days,
            "timezone": "auto",
        }
        data = await self._fetch_with_retry(params)
        hourly_raw = data.get("hourly", {})
        times = hourly_raw.get("time", [])
        aqis = hourly_raw.get("us_aqi", [])
        pm25s = hourly_raw.get("pm2_5", [])
        pm10s = hourly_raw.get("pm10", [])
        no2s = hourly_raw.get("nitrogen_dioxide", [])
        o3s = hourly_raw.get("ozone", [])

        points: list[HourlyForecastPoint] = []
        for i in range(len(times)):
            val_aqi = int(aqis[i]) if aqis and aqis[i] is not None else 0
            points.append(
                HourlyForecastPoint(
                    timestamp=datetime.fromisoformat(times[i]),
                    aqi=val_aqi,
                    aqi_category=calculate_us_aqi_category(val_aqi),
                    pm2_5=float(pm25s[i] or 0.0),
                    pm10=float(pm10s[i] or 0.0),
                    no2=float(no2s[i]) if no2s and no2s[i] is not None else None,
                    o3=float(o3s[i]) if o3s and o3s[i] is not None else None,
                )
            )

        result = AirQualityForecast(
            latitude=data.get("latitude", latitude),
            longitude=data.get("longitude", longitude),
            aqi_standard=AQIStandard.US_AQI,
            hourly=points,
            source_metadata=SourceMetadata(
                provider="Open-Meteo",
                data_type=DataSourceType.FORECAST,
                source_resolution="11km atmospheric CAMS grid",
                observed_at=datetime.now(UTC),
            ),
        )
        self._cache[key] = (now, result)
        return result
