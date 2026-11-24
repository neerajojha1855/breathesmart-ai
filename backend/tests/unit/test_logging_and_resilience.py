"""Unit tests verifying sensitive logging redaction, custom exceptions, and fallback triggers."""
import logging
from datetime import datetime, timezone
from app.core.logging import SanitizeFormatter, setup_logging
from app.core.exceptions import (
    BreatheSmartException,
    InvalidSessionError,
    SessionExpiredError,
    CSRFError,
    AirQualityProviderError,
    GeocodingProviderError,
    AIProviderError,
)
from app.ai.fallback_generator import DeterministicFallbackGenerator
from app.schemas.air_quality import (
    AQICategory,
    AQIStandard,
    DataSourceType,
    NormalizedAirQuality,
    PollutantMeasurement,
    Pollutants,
    SourceMetadata,
)


def test_credential_redaction_filter():
    formatter = SanitizeFormatter(fmt="%(message)s")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Connecting with key gsk_abc1234567890def and bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 and npg_Z1KODxTuIcR6",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    assert "gsk_abc1234567890def" not in formatted
    assert "npg_Z1KODxTuIcR6" not in formatted
    assert "[REDACTED]" in formatted

    # Test setup_logging execution
    setup_logging()


def test_custom_domain_exceptions():
    base_exc = BreatheSmartException("Internal", code="CUSTOM_CODE", details={"k": "v"})
    assert base_exc.code == "CUSTOM_CODE"
    assert base_exc.details["k"] == "v"

    sess_exc = InvalidSessionError()
    assert sess_exc.code == "INVALID_SESSION"

    exp_exc = SessionExpiredError()
    assert exp_exc.code == "SESSION_EXPIRED"

    csrf_exc = CSRFError()
    assert csrf_exc.code == "CSRF_VALIDATION_FAILED"

    aq_exc = AirQualityProviderError("Open-Meteo timeout")
    assert aq_exc.code == "AIR_QUALITY_PROVIDER_ERROR"

    geo_exc = GeocodingProviderError("Geocoding failed")
    assert geo_exc.code == "GEOCODING_PROVIDER_ERROR"

    ai_exc = AIProviderError("Groq quota exceeded")
    assert ai_exc.code == "AI_PROVIDER_ERROR"


def test_fallback_generator_various_aqi_levels():
    def make_aqi(aqi_val: int, cat: AQICategory) -> NormalizedAirQuality:
        return NormalizedAirQuality(
            latitude=28.6139,
            longitude=77.2090,
            timezone="UTC",
            aqi=aqi_val,
            aqi_standard=AQIStandard.US_AQI,
            aqi_category=cat,
            dominant_pollutant="pm2_5",
            pollutants=Pollutants(
                pm2_5=PollutantMeasurement(value=float(aqi_val), unit="µg/m³"),
            ),
            source_metadata=SourceMetadata(
                provider="Open-Meteo",
                data_type=DataSourceType.MODELED,
                observed_at=datetime.now(timezone.utc),
            ),
        )

    # Moderate
    mod_plan = DeterministicFallbackGenerator.generate_plan(make_aqi(75, AQICategory.MODERATE))
    assert mod_plan is not None

    # Unhealthy
    unh_plan = DeterministicFallbackGenerator.generate_plan(make_aqi(160, AQICategory.UNHEALTHY))
    assert unh_plan is not None

    # Hazardous
    haz_plan = DeterministicFallbackGenerator.generate_plan(make_aqi(350, AQICategory.HAZARDOUS))
    assert haz_plan is not None
