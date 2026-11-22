from typing import Any

class BreatheSmartException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

class InvalidSessionError(BreatheSmartException):
    def __init__(self, message: str = "Invalid or missing session") -> None:
        super().__init__(message=message, code="INVALID_SESSION")

class SessionExpiredError(BreatheSmartException):
    def __init__(self, message: str = "Session has expired") -> None:
        super().__init__(message=message, code="SESSION_EXPIRED")

class CSRFError(BreatheSmartException):
    def __init__(self, message: str = "CSRF verification failed") -> None:
        super().__init__(message=message, code="CSRF_VALIDATION_FAILED")


class AirQualityProviderError(BreatheSmartException):
        def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
            super().__init__(message=message, code="AIR_QUALITY_PROVIDER_ERROR", details=details)

class GeocodingProviderError(BreatheSmartException):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="GEOCODING_PROVIDER_ERROR", details=details)

class AIProviderError(BreatheSmartException):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="AI_PROVIDER_ERROR", details=details)