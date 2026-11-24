import logging

import httpx
from fastapi import APIRouter, Query

from app.ai.groq_client import GroqAIService
from app.ai.schemas import AIChatRequest, AIChatResponse
from app.core.exceptions import BreatheSmartException
from app.providers.air_quality.open_meteo import OpenMeteoAirQualityProvider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])
ai_service = GroqAIService()
aq_provider = OpenMeteoAirQualityProvider()


@router.post("/chat", response_model=AIChatResponse)
async def chat_with_assistant(
    req: AIChatRequest,
    latitude: float | None = Query(default=None, ge=-90.0, le=90.0),
    longitude: float | None = Query(default=None, ge=-180.0, le=180.0),
):
    """Conversational AI assistant grounded in live environmental context."""
    aqi_data = None
    if latitude is not None and longitude is not None:
        try:
            aqi_data = await aq_provider.get_current_air_quality(latitude, longitude)
        except (BreatheSmartException, httpx.HTTPError, ValueError) as exc:
            logger.warning(
                "Unable to fetch live AQI context for assistant (%s, %s): %s",
                latitude,
                longitude,
                exc,
            )

    return await ai_service.chat_assistant(req, aqi_data=aqi_data)
