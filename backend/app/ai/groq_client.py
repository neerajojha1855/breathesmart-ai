"""Groq GenAI client abstraction with structured output validation and automatic fallback."""

import json
import logging
from typing import Any
from groq import AsyncGroq
from app.ai.fallback_generator import DeterministicFallbackGenerator
from app.ai.prompts import ACTION_PLAN_SYSTEM_PROMPT, CHAT_ASSISTANT_SYSTEM_PROMPT
from app.ai.schemas import (
    AIChatMessage,
    AIChatRequest,
    AIChatResponse,
    BreatheSmartActionPlanResponse,
)
from app.core.config import settings
from app.schemas.air_quality import NormalizedAirQuality

logger = logging.getLogger(__name__)


class GroqAIService:
    """Service orchestrating Groq LLM requests with strict schema constraints and fallback resilience."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL_NAME
        self.client = AsyncGroq(api_key=self.api_key) if self.api_key else None

    async def generate_action_plan(
        self,
        aqi_data: NormalizedAirQuality,
        user_preferences: dict[str, Any] | None = None,
    ) -> BreatheSmartActionPlanResponse:
        """Generate a personalized action plan with strict Pydantic validation."""
        if not self.client:
            logger.warning("GROQ_API_KEY is not configured; using deterministic fallback engine.")
            return DeterministicFallbackGenerator.generate_plan(aqi_data, user_preferences)

        user_content = json.dumps(
            {
                "environmental_context": {
                    "aqi": aqi_data.aqi,
                    "standard": aqi_data.aqi_standard.value,
                    "category": aqi_data.aqi_category.value,
                    "pollutants": {
                        "pm2_5": aqi_data.pollutants.pm2_5.value if aqi_data.pollutants.pm2_5 else None,
                        "pm10": aqi_data.pollutants.pm10.value if aqi_data.pollutants.pm10 else None,
                        "no2": aqi_data.pollutants.no2.value if aqi_data.pollutants.no2 else None,
                        "o3": aqi_data.pollutants.o3.value if aqi_data.pollutants.o3 else None,
                    },
                    "coordinates": {"lat": aqi_data.latitude, "lon": aqi_data.longitude},
                    "observed_at": str(aqi_data.source_metadata.observed_at),
                },
                "user_preferences": user_preferences or {},
            }
        )

        for attempt in range(settings.AI_MAX_RETRIES + 1):
            try:
                chat_completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": ACTION_PLAN_SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"Analyze this environmental data and return the action plan JSON:\n{user_content}",
                        },
                    ],
                    response_format={"type": "json_object"},
                    timeout=settings.AI_REQUEST_TIMEOUT_SECONDS,
                    temperature=0.2,
                )
                raw_response = chat_completion.choices[0].message.content or "{}"
                parsed_json = json.loads(raw_response)
                # Handle wrapped "response" key if present
                if "response" in parsed_json and isinstance(parsed_json["response"], dict):
                    parsed_json = parsed_json["response"]

                # Normalize if model used grouped exposure/emissions keys
                if "recommendations" not in parsed_json and any(k in parsed_json for k in ["personal_exposure", "direct_emissions"]):
                    recs = []
                    for item in parsed_json.get("personal_exposure", []):
                        if isinstance(item, dict):
                            item.setdefault("category", "outdoor")
                            item.setdefault("impact_type", "exposure")
                            item.setdefault("priority", "high")
                            item.setdefault("confidence", "high")
                            item.setdefault("recommended_time", "All Day")
                            item.setdefault("reason", "Particulate exposure avoidance")
                            item.setdefault("expected_impact", "Reduces inhalation of fine particulates")
                            recs.append(item)
                    for item in parsed_json.get("direct_emissions", []):
                        if isinstance(item, dict):
                            item.setdefault("category", "sustainability")
                            item.setdefault("impact_type", "emissions")
                            item.setdefault("priority", "medium")
                            item.setdefault("confidence", "high")
                            item.setdefault("recommended_time", "Daily")
                            item.setdefault("reason", "Carbon footprint reduction")
                            item.setdefault("expected_impact", "Measurable CO2e reduction")
                            recs.append(item)
                    parsed_json["recommendations"] = recs
                    parsed_json.setdefault("summary", f"Daily air quality plan for AQI {aqi_data.aqi}")
                    parsed_json.setdefault("explanation", f"Current air quality is {aqi_data.aqi_category.value} with dominant pollutant {aqi_data.dominant_pollutant}.")
                    parsed_json.setdefault("risk_level", "severe" if aqi_data.aqi >= 200 else ("high" if aqi_data.aqi >= 150 else ("moderate" if aqi_data.aqi >= 50 else "good")))

                return BreatheSmartActionPlanResponse.model_validate(parsed_json)
            except Exception as exc:
                logger.warning(
                    f"Groq generation attempt {attempt + 1} failed: {exc}. Retrying or falling back."
                )

        logger.error("All Groq generation attempts failed. Activating deterministic fallback.")
        return DeterministicFallbackGenerator.generate_plan(aqi_data, user_preferences)

    async def chat_assistant(
        self,
        request: AIChatRequest,
        aqi_data: NormalizedAirQuality | None = None,
    ) -> AIChatResponse:
        """Process conversational user inquiry with prompt-injection defense and context injection."""
        if not self.client:
            return AIChatResponse(
                message="AI service is running in offline fallback mode. Check back shortly for conversational assistant.",
                suggested_followups=["What is today's AQI?", "When should I open my windows?"],
                context_sources=["Local Fallback Engine"],
            )

        context_str = ""
        if aqi_data:
            context_str = (
                f"CURRENT AIR QUALITY CONTEXT:\n"
                f"- AQI: {aqi_data.aqi} ({aqi_data.aqi_category.value}, standard: {aqi_data.aqi_standard.value})\n"
                f"- PM2.5: {aqi_data.pollutants.pm2_5.value if aqi_data.pollutants.pm2_5 else 'N/A'} µg/m³\n"
                f"- PM10: {aqi_data.pollutants.pm10.value if aqi_data.pollutants.pm10 else 'N/A'} µg/m³\n"
            )

        messages: list[dict[str, str]] = [
            {"role": "system", "content": f"{CHAT_ASSISTANT_SYSTEM_PROMPT}\n\n{context_str}"}
        ]

        for hist in request.history[-6:]:
            messages.append({"role": hist.role, "content": hist.content})

        messages.append({"role": "user", "content": request.message})

        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                timeout=settings.AI_REQUEST_TIMEOUT_SECONDS,
                temperature=0.3,
            )
            raw_text = completion.choices[0].message.content or "{}"
            data = json.loads(raw_text)
            return AIChatResponse(
                message=data.get("message", "Unable to formulate a response."),
                suggested_followups=data.get("suggested_followups", []),
                context_sources=["Open-Meteo Air Quality", "Groq gpt-oss-120b"],
            )
        except Exception as exc:
            logger.error(f"Chat assistant failed: {exc}")
            return AIChatResponse(
                message="I am having trouble connecting to the environmental AI service right now. Please consult the Daily Action Plan for verified recommendations.",
                suggested_followups=["Show today's recommendations", "What is the PM2.5 level?"],
                context_sources=["Fallback Engine"],
            )
