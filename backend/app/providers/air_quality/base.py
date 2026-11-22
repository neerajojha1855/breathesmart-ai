"""Abstract base class for environmental air quality data providers."""

from abc import ABC, abstractmethod
from app.schemas.air_quality import AirQualityForecast, NormalizedAirQuality


class BaseAirQualityProvider(ABC):
    """Abstract interface decoupling domain logic from external environmental APIs."""

    @abstractmethod
    async def get_current_air_quality(
        self, latitude: float, longitude: float
    ) -> NormalizedAirQuality:
        """Fetch and normalize current air quality for coordinates."""
        pass

    @abstractmethod
    async def get_forecast(
        self, latitude: float, longitude: float, forecast_days: int = 5
    ) -> AirQualityForecast:
        """Fetch hourly air quality forecast."""
        pass
