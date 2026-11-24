export type AQICategory =
  | 'good'
  | 'moderate'
  | 'unhealthy_for_sensitive_groups'
  | 'unhealthy'
  | 'very_unhealthy'
  | 'hazardous'
  | 'unknown';

export interface PollutantMeasurement {
  value: number;
  unit: string;
  category: AQICategory;
}

export interface Pollutants {
  pm2_5?: PollutantMeasurement;
  pm10?: PollutantMeasurement;
  no2?: PollutantMeasurement;
  so2?: PollutantMeasurement;
  o3?: PollutantMeasurement;
  co?: PollutantMeasurement;
}

export interface SourceMetadata {
  provider: string;
  data_type: 'measured' | 'modeled' | 'forecast';
  source_resolution: string;
  observed_at: string;
  freshness_seconds: number;
  license_attribution: string;
}

export interface NormalizedAirQuality {
  latitude: number;
  longitude: number;
  timezone: string;
  aqi: number;
  aqi_standard: 'US_AQI' | 'EU_AQI' | 'CPCB';
  aqi_category: AQICategory;
  dominant_pollutant: string;
  pollutants: Pollutants;
  source_metadata: SourceMetadata;
}

export interface HourlyForecastPoint {
  timestamp: string;
  aqi: number;
  aqi_category: AQICategory;
  pm2_5: number;
  pm10: number;
  no2?: number;
  o3?: number;
}

export interface AirQualityForecast {
  latitude: number;
  longitude: number;
  aqi_standard: string;
  hourly: HourlyForecastPoint[];
  source_metadata: SourceMetadata;
}

export interface ActionRecommendationItem {
  title: string;
  category: 'outdoor' | 'indoor' | 'commute' | 'sustainability';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  recommended_time: string;
  action: string;
  reason: string;
  expected_impact: string;
  impact_type: 'exposure' | 'emissions' | 'energy' | 'qualitative';
  confidence: 'low' | 'medium' | 'high';
  assumptions: string[];
}

export interface BreatheSmartActionPlanResponse {
  summary: string;
  risk_level: 'good' | 'moderate' | 'high' | 'severe' | 'unknown';
  explanation: string;
  recommendations: ActionRecommendationItem[];
  limitations: string[];
  safety_notes: string[];
}

export interface LocationSearchResult {
  id?: number;
  name: string;
  latitude: number;
  longitude: number;
  country: string;
  admin1?: string;
  country_code?: string;
  timezone: string;
}

export interface CommuteShiftImpact {
  baseline_mode: string;
  alternative_mode: string;
  distance_km: number;
  trips_per_week: number;
  baseline_co2e_kg: number;
  alternative_co2e_kg: number;
  weekly_co2e_saved_kg: number;
  annual_co2e_saved_kg: number;
  trees_equivalent_annual: number;
  particulate_exposure_benefit: string;
  direct_emissions_benefit: string;
  methodology: string;
  assumptions: string[];
}

export interface LocationState {
  city: string;
  country: string;
  latitude: number;
  longitude: number;
  is_primary?: boolean;
}

export interface VentilationRecommendation {
  suitability: 'optimal' | 'controlled' | 'unfavorable' | 'hazardous' | string;
  can_open_windows: boolean;
  recommended_window: string;
  max_duration_minutes: number;
  rationale: string;
  co2_management_warning: string;
  action_steps: string[];
}

export interface PurifierRecommendation {
  has_purifier: boolean;
  recommended_mode: string;
  filter_health_guidance: string;
  target_pm25_indoor: string;
  estimated_air_changes_per_hour: number;
}

export interface IndoorAirAdvisorReport {
  ventilation: VentilationRecommendation;
  purification: PurifierRecommendation;
  cooking_safety_checklist: string[];
  combustion_hazards_to_avoid: string[];
}

export interface UserProfile {
  id: string;
  session_id: string;
  preferred_language: string;
  household_preferences: Record<string, unknown>;
  commuting_preferences: Record<string, unknown>;
  indoor_environment_preferences: Record<string, unknown>;
  sensitive_group_consent: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface AIChatResponse {
  message: string;
  suggested_followups: string[];
  context_sources: string[];
}
