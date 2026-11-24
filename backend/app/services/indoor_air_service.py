"""Indoor Air Quality Service: Scientifically safe ventilation schedules, HEPA purification, and combustion hazard mitigation."""

from enum import Enum

from app.schemas.air_quality import AirQualityForecast, NormalizedAirQuality
from pydantic import BaseModel, Field


class VentilationSuitability(str, Enum):
    OPTIMAL = "optimal"  # Clean outdoor air, open freely
    CONTROLLED = "controlled"  # Limited window (20-30 min) during afternoon solar peak
    UNFAVORABLE = "unfavorable"  # Keep windows closed; run air purifier; ventilate only briefly if CO2 rises
    HAZARDOUS = "hazardous"  # Strict home sealing with mechanical HEPA filtration


class VentilationRecommendation(BaseModel):
    suitability: VentilationSuitability
    can_open_windows: bool
    recommended_window: str = Field(
        description="Optimal time range e.g. '01:00 PM - 02:30 PM'"
    )
    max_duration_minutes: int
    rationale: str
    co2_management_warning: str
    action_steps: list[str]


class PurifierRecommendation(BaseModel):
    has_purifier: bool
    recommended_mode: str
    filter_health_guidance: str
    target_pm25_indoor: str
    estimated_air_changes_per_hour: float


class IndoorAirAdvisorReport(BaseModel):
    ventilation: VentilationRecommendation
    purification: PurifierRecommendation
    cooking_safety_checklist: list[str]
    combustion_hazards_to_avoid: list[str]


class IndoorAirService:
    """Provides evidence-based indoor air quality recommendations balancing outdoor smog vs indoor CO2 accumulation."""

    @classmethod
    def evaluate_ventilation(
        cls,
        aqi_data: NormalizedAirQuality,
        forecast: AirQualityForecast | None = None,
    ) -> VentilationRecommendation:
        aqi = aqi_data.aqi
        pm25 = aqi_data.pollutants.pm2_5.value if aqi_data.pollutants.pm2_5 else 0.0

        if aqi <= 50 and pm25 <= 12.0:
            return VentilationRecommendation(
                suitability=VentilationSuitability.OPTIMAL,
                can_open_windows=True,
                recommended_window="All day (Continuous)",
                max_duration_minutes=240,
                rationale="Outdoor air is pristine. Full natural cross-ventilation maintains fresh indoor air and low CO2.",
                co2_management_warning="Indoor CO2 will remain safely below 600 ppm with open windows.",
                action_steps=[
                    "Open windows on opposite sides of the living space to create cross-breeze.",
                    "Air out bedrooms and living rooms completely.",
                ],
            )
        elif aqi <= 100:
            return VentilationRecommendation(
                suitability=VentilationSuitability.CONTROLLED,
                can_open_windows=True,
                recommended_window="11:00 AM - 04:00 PM (Solar Peak)",
                max_duration_minutes=45,
                rationale="Moderate pollution outdoors. Midday solar heating raises the atmospheric boundary layer, reducing surface pollution.",
                co2_management_warning="Open windows for 30-45 minutes to prevent stale air and indoor moisture buildup, then reclose.",
                action_steps=[
                    "Open windows between 11:00 AM and 04:00 PM when particulate levels are lowest.",
                    "Close windows during morning and evening rush hours.",
                ],
            )
        elif aqi <= 200:
            return VentilationRecommendation(
                suitability=VentilationSuitability.UNFAVORABLE,
                can_open_windows=False,
                recommended_window="01:00 PM - 02:00 PM (Brief Flush Only)",
                max_duration_minutes=20,
                rationale=(
                    "Outdoor air is unhealthy. However, permanently sealing a occupied home causes dangerous indoor CO2 buildup "
                    "(often exceeding 1,500-2,000 ppm), causing fatigue, headaches, and cognitive decline."
                ),
                co2_management_warning=(
                    "Perform a brief 15-20 minute rapid cross-ventilation flush during the early afternoon lull, "
                    "then immediately seal the home and run your HEPA purifier on maximum speed for 30 minutes to capture infiltrated particles."
                ),
                action_steps=[
                    "Keep windows firmly closed during morning and nighttime inversion periods.",
                    "Conduct a single 15-20 minute rapid flush between 01:00 PM and 02:00 PM.",
                    "Turn air purifier to High/Turbo immediately after closing windows.",
                ],
            )
        else:
            return VentilationRecommendation(
                suitability=VentilationSuitability.HAZARDOUS,
                can_open_windows=False,
                recommended_window="Not recommended (Keep sealed)",
                max_duration_minutes=0,
                rationale="Hazardous outdoor particulate concentrations. Ambient PM2.5 infiltration poses acute respiratory risk.",
                co2_management_warning="If indoor air feels heavy or stale after 8+ hours, crack an interior door or run a kitchen exhaust briefly with bedroom doors closed.",
                action_steps=[
                    "Keep all external doors and windows sealed.",
                    "Apply weather-stripping or damp towels along unsealed door thresholds if drafts occur.",
                    "Run HEPA air purifiers continuously on auto or medium-high mode.",
                ],
            )

    @classmethod
    def evaluate_purification(
        cls,
        aqi_data: NormalizedAirQuality,
        has_purifier: bool = True,
        room_area_sqm: float = 25.0,
    ) -> PurifierRecommendation:
        aqi = aqi_data.aqi

        if aqi > 200:
            mode = "High / Turbo Mode (Continuous)"
            target = "< 15 µg/m³"
            ach = 5.0
        elif aqi > 100:
            mode = "Medium / Auto Mode"
            target = "< 25 µg/m³"
            ach = 3.5
        else:
            mode = "Sleep / Low Mode"
            target = "< 10 µg/m³"
            ach = 2.0

        return PurifierRecommendation(
            has_purifier=has_purifier,
            recommended_mode=mode,
            filter_health_guidance="Inspect pre-filter mesh bi-weekly; vacuum accumulated surface dust. Replace true HEPA H13 cartridge every 6 months during severe smog season.",
            target_pm25_indoor=target,
            estimated_air_changes_per_hour=ach,
        )

    @classmethod
    def generate_full_advisor_report(
        cls,
        aqi_data: NormalizedAirQuality,
        has_purifier: bool = True,
        forecast: AirQualityForecast | None = None,
    ) -> IndoorAirAdvisorReport:
        ventilation = cls.evaluate_ventilation(aqi_data, forecast)
        purification = cls.evaluate_purification(aqi_data, has_purifier=has_purifier)

        cooking_checklist = [
            "Always activate range hood exhaust before turning on gas stoves; keep running for 5 minutes after cooking.",
            "Use lids on pots and pans to minimize oil aerosolization and steam emissions.",
            "Avoid high-temperature deep frying or pan-searing during severe outdoor smog episodes.",
            "Cook on rear stove burners when possible (range hoods capture rear-burner fumes ~30% more effectively).",
        ]

        combustion_hazards = [
            "Prohibit indoor incense, scented candles, and mosquito coils (a single incense stick emits PM2.5 equivalent to several cigarettes).",
            "Avoid indoor biomass, kerosene space heaters, or unvented fireplace combustion.",
            "Avoid aerosol air fresheners and harsh chemical spray cleaners, which generate secondary organic aerosols.",
            "Do not smoke or allow vaping indoors.",
        ]

        return IndoorAirAdvisorReport(
            ventilation=ventilation,
            purification=purification,
            cooking_safety_checklist=cooking_checklist,
            combustion_hazards_to_avoid=combustion_hazards,
        )
