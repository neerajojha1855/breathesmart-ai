"""Sustainability Service: Scientifically grounded emission calculations and travel mode comparisons."""

from dataclasses import dataclass
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class TransportMode(str, Enum):
    PETROL_CAR = "petrol_car"
    DIESEL_CAR = "diesel_car"
    ELECTRIC_CAR = "electric_car"
    MOTORCYCLE = "motorcycle"
    METRO_TRAIN = "metro_train"
    CITY_BUS = "city_bus"
    CYCLING = "cycling"
    WALKING = "walking"


# Standardized Emission Factors (kg CO2e per passenger-km) based on UK DEFRA & US EPA
EMISSION_FACTORS_KG_CO2E_PER_KM: dict[TransportMode, float] = {
    TransportMode.PETROL_CAR: 0.171,
    TransportMode.DIESEL_CAR: 0.165,
    TransportMode.ELECTRIC_CAR: 0.047,  # Average grid carbon intensity
    TransportMode.MOTORCYCLE: 0.114,
    TransportMode.CITY_BUS: 0.089,
    TransportMode.METRO_TRAIN: 0.028,
    TransportMode.CYCLING: 0.000,
    TransportMode.WALKING: 0.000,
}


class CommuteShiftImpact(BaseModel):
    baseline_mode: TransportMode
    alternative_mode: TransportMode
    distance_km: float
    trips_per_week: int = 10  # 5 round trips typical work week
    baseline_co2e_kg: float
    alternative_co2e_kg: float
    weekly_co2e_saved_kg: float
    annual_co2e_saved_kg: float
    trees_equivalent_annual: float
    particulate_exposure_benefit: str
    direct_emissions_benefit: str
    methodology: str
    assumptions: list[str]


class SustainabilityService:
    """Calculates verifiable environmental emission savings and personal exposure benefits."""

    @classmethod
    def calculate_commute_shift(
        cls,
        baseline_mode: TransportMode,
        alternative_mode: TransportMode,
        distance_km: float,
        trips_per_week: int = 10,
    ) -> CommuteShiftImpact:
        if distance_km <= 0:
            raise ValueError("Distance must be greater than 0 km")

        baseline_factor = EMISSION_FACTORS_KG_CO2E_PER_KM[baseline_mode]
        alternative_factor = EMISSION_FACTORS_KG_CO2E_PER_KM[alternative_mode]

        baseline_per_trip = baseline_factor * distance_km
        alt_per_trip = alternative_factor * distance_km

        trip_saving_kg = max(0.0, baseline_per_trip - alt_per_trip)
        weekly_saved_kg = round(trip_saving_kg * trips_per_week, 2)
        annual_saved_kg = round(weekly_saved_kg * 48, 2)  # 48 working weeks per year

        # 1 mature urban tree absorbs approximately 21.77 kg CO2 per year (EPA standard)
        trees_eq = round(annual_saved_kg / 21.77, 1)

        # Clear distinction between personal exposure vs direct environmental emissions
        if alternative_mode in (TransportMode.METRO_TRAIN,):
            exposure_benefit = (
                "Subway / underground trains provide an enclosed, filtered micro-environment, "
                "reducing direct inhalation of roadside particulate matter (PM2.5 and ultrafine particles) by up to 50% "
                "compared to congested road vehicles."
            )
        elif alternative_mode in (TransportMode.CYCLING, TransportMode.WALKING):
            exposure_benefit = (
                "Active travel increases ventilation rate (breathing volume). During moderate to severe smog episodes, "
                "active travel along congested arterial roads increases personal particulate dose. "
                "Recommendation: Choose low-traffic green corridors or shift to electric metro during high AQI alerts."
            )
        else:
            exposure_benefit = (
                "Bus transit reduces private vehicle density on the road corridor, though personal exposure depends on cabin filtration."
            )

        emissions_benefit = (
            f"Prevents {trip_saving_kg:.2f} kg CO2e per trip ({weekly_saved_kg:.1f} kg CO2e/week). "
            f"Equivalent to planting {trees_eq:.1f} mature trees annually."
        )

        return CommuteShiftImpact(
            baseline_mode=baseline_mode,
            alternative_mode=alternative_mode,
            distance_km=distance_km,
            trips_per_week=trips_per_week,
            baseline_co2e_kg=round(baseline_per_trip, 3),
            alternative_co2e_kg=round(alt_per_trip, 3),
            weekly_co2e_saved_kg=weekly_saved_kg,
            annual_co2e_saved_kg=annual_saved_kg,
            trees_equivalent_annual=trees_eq,
            particulate_exposure_benefit=exposure_benefit,
            direct_emissions_benefit=emissions_benefit,
            methodology="Based on UK DEFRA (Department for Environment, Food & Rural Affairs) Greenhouse Gas Reporting Conversion Factors and US EPA Carbon Equivalencies.",
            assumptions=[
                f"Baseline {baseline_mode.value}: {baseline_factor:.3f} kg CO2e/p-km.",
                f"Alternative {alternative_mode.value}: {alternative_factor:.3f} kg CO2e/p-km.",
                "Assumes average passenger occupancy for public transit.",
                "Strict distinction: CO2e reduction measures climate footprint; PM2.5 exposure measures acute health dose.",
            ],
        )
