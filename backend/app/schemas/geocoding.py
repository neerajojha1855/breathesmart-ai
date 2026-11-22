"""Pydantic schemas for location geocoding results."""

from pydantic import BaseModel


class LocationSearchResult(BaseModel):
    id: int | None = None
    name: str
    latitude: float
    longitude: float
    country: str
    admin1: str | None = None
    country_code: str | None = None
    timezone: str = "UTC"
