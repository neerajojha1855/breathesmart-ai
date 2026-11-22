"""Open-Meteo Geocoding provider for location search and coordinate lookup."""

import time
from typing import Any
import httpx
from app.core.exceptions import GeocodingProviderError
from app.schemas.geocoding import LocationSearchResult


class OpenMeteoGeocodingProvider:
    BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"
    CACHE_TTL_SECONDS = 3600  # 1 hour

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(timeout=10.0)
        self._cache: dict[str, tuple[float, list[LocationSearchResult]]] = {}

    async def search_locations(self, query: str, count: int = 5) -> list[LocationSearchResult]:
        q = query.strip().lower()
        if len(q) < 2:
            return []

        now = time.time()
        if q in self._cache and (now - self._cache[q][0]) < self.CACHE_TTL_SECONDS:
            return self._cache[q][1]

        try:
            response = await self._client.get(
                self.BASE_URL,
                params={"name": query, "count": count, "language": "en", "format": "json"},
            )
            if response.status_code != 200:
                raise GeocodingProviderError(f"Geocoding service returned status {response.status_code}")

            data = response.json()
            results_raw = data.get("results", []) or []
            results: list[LocationSearchResult] = []
            for item in results_raw:
                results.append(
                    LocationSearchResult(
                        id=item.get("id"),
                        name=item.get("name"),
                        latitude=item.get("latitude"),
                        longitude=item.get("longitude"),
                        country=item.get("country", ""),
                        admin1=item.get("admin1"),
                        country_code=item.get("country_code"),
                        timezone=item.get("timezone", "UTC"),
                    )
                )
            self._cache[q] = (now, results)
            return results
        except httpx.RequestError as exc:
            raise GeocodingProviderError(f"Network error contacting geocoding service: {exc}") from exc
