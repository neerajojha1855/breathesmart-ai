"""Groq GenAI client abstraction with structured output validation and automatic fallback."""

import json
import logging
from typing import Any

from groq import AsyncGroq

from app.ai.fallback_generator import DeterministicFallbackGenerator
from app.ai.prompts import ACTION_PLAN_SYSTEM_PROMPT, CHAT_ASSISTANT_SYSTEM_PROMPT
from app.ai.schemas import (
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

    @staticmethod
    def _derive_risk_level(aqi: int) -> str:
        """Map numeric US AQI value to discrete risk level string."""
        if aqi >= 200:
            return "severe"
        if aqi >= 150:
            return "high"
        if aqi >= 50:
            return "moderate"
        return "good"

    @staticmethod
    def _build_action_plan_context(
        aqi_data: NormalizedAirQuality,
        user_preferences: dict[str, Any] | None = None,
    ) -> str:
        """Serialize verified AQI readings and user preferences for LLM grounding."""
        p = aqi_data.pollutants
        return json.dumps(
            {
                "environmental_context": {
                    "aqi": aqi_data.aqi,
                    "standard": aqi_data.aqi_standard.value,
                    "category": aqi_data.aqi_category.value,
                    "pollutants": {
                        "pm2_5": p.pm2_5.value if p.pm2_5 else None,
                        "pm10": p.pm10.value if p.pm10 else None,
                        "no2": p.no2.value if p.no2 else None,
                        "o3": p.o3.value if p.o3 else None,
                    },
                    "coordinates": {
                        "lat": aqi_data.latitude,
                        "lon": aqi_data.longitude,
                    },
                    "observed_at": str(aqi_data.source_metadata.observed_at),
                },
                "user_preferences": user_preferences or {},
            }
        )

    @classmethod
    def _normalize_action_plan_payload(
        cls,
        parsed_json: dict[str, Any],
        aqi_data: NormalizedAirQuality,
    ) -> dict[str, Any]:
        """Normalize legacy or wrapped LLM JSON payloads to match BreatheSmartActionPlanResponse."""
        if "response" in parsed_json and isinstance(parsed_json["response"], dict):
            parsed_json = parsed_json["response"]

        if "recommendations" in parsed_json or not any(
            k in parsed_json for k in ("personal_exposure", "direct_emissions")
        ):
            return parsed_json

        group_defaults: tuple[tuple[str, dict[str, str]], ...] = (
            (
                "personal_exposure",
                {
                    "category": "outdoor",
                    "impact_type": "exposure",
                    "priority": "high",
                    "confidence": "high",
                    "recommended_time": "All Day",
                    "reason": "Particulate exposure avoidance",
                    "expected_impact": "Reduces inhalation of fine particulates",
                },
            ),
            (
                "direct_emissions",
                {
                    "category": "sustainability",
                    "impact_type": "emissions",
                    "priority": "medium",
                    "confidence": "high",
                    "recommended_time": "Daily",
                    "reason": "Carbon footprint reduction",
                    "expected_impact": "Measurable CO2e reduction",
                },
            ),
        )

        recs: list[dict[str, Any]] = []
        for group_key, defaults in group_defaults:
            for item in parsed_json.get(group_key, []):
                if isinstance(item, dict):
                    for field, default_val in defaults.items():
                        item.setdefault(field, default_val)
                    recs.append(item)

        parsed_json["recommendations"] = recs
        parsed_json.setdefault("summary", f"Daily air quality plan for AQI {aqi_data.aqi}")
        parsed_json.setdefault(
            "explanation",
            f"Current air quality is {aqi_data.aqi_category.value} with dominant pollutant {aqi_data.dominant_pollutant}.",
        )
        parsed_json.setdefault("risk_level", cls._derive_risk_level(aqi_data.aqi))
        return parsed_json

    async def generate_action_plan(
        self,
        aqi_data: NormalizedAirQuality,
        user_preferences: dict[str, Any] | None = None,
    ) -> BreatheSmartActionPlanResponse:
        """Generate a personalized action plan with strict Pydantic validation."""
        if not self.client:
            logger.warning(
                "GROQ_API_KEY is not configured; using deterministic fallback engine."
            )
            return DeterministicFallbackGenerator.generate_plan(
                aqi_data, user_preferences
            )

        user_content = self._build_action_plan_context(aqi_data, user_preferences)

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
                parsed_json = self._normalize_action_plan_payload(
                    json.loads(raw_response), aqi_data
                )
                return BreatheSmartActionPlanResponse.model_validate(parsed_json)
            except Exception as exc:
                logger.warning(
                    f"Groq generation attempt {attempt + 1} failed: {exc}. Retrying or falling back."
                )

        logger.error(
            "All Groq generation attempts failed. Activating deterministic fallback."
        )
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
                suggested_followups=[
                    "What is today's AQI?",
                    "When should I open my windows?",
                ],
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
            {
                "role": "system",
                "content": f"{CHAT_ASSISTANT_SYSTEM_PROMPT}\n\n{context_str}",
            }
        ]

        for hist in request.history[-6:]:
            messages.append({"role": hist.role, "content": hist.content})

        messages.append({"role": "user", "content": request.message})

        try:
            completion = await self.client.chat.completions.create(  # type: ignore[call-overload]
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
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
                suggested_followups=[
                    "Show today's recommendations",
                    "What is the PM2.5 level?",
                ],
                context_sources=["Fallback Engine"],
            )
