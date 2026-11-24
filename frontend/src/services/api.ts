import type {
  AirQualityForecast,
  BreatheSmartActionPlanResponse,
  CommuteShiftImpact,
  LocationSearchResult,
  NormalizedAirQuality,
} from '../types';

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  headers.set('Accept', 'application/json');

  if (options.method && !['GET', 'HEAD'].includes(options.method.toUpperCase())) {
    headers.set('Content-Type', 'application/json');
    const csrf = getCookie('breathe_smart_csrf');
    if (csrf) {
      headers.set('X-CSRF-Token', csrf);
    }
  }

  const res = await fetch(path, {
    ...options,
    headers,
    credentials: 'include',
  });

  if (!res.ok) {
    let errorDetail = 'Network request failed';
    try {
      const errJson = await res.json();
      errorDetail = errJson?.error?.message || errJson?.detail || errorDetail;
    } catch {
      // Non-JSON response
    }
    throw new Error(errorDetail);
  }

  if (res.status === 204) {
    return {} as T;
  }

  return res.json();
}

export const api = {
  // Locations
  searchLocations: (q: string) =>
    request<LocationSearchResult[]>(`/api/v1/locations/search?q=${encodeURIComponent(q)}`),

  // Air Quality
  getCurrentAirQuality: (lat: number, lon: number) =>
    request<NormalizedAirQuality>(`/api/v1/air-quality/current?latitude=${lat}&longitude=${lon}`),

  getAirQualityForecast: (lat: number, lon: number, days = 5) =>
    request<AirQualityForecast>(`/api/v1/air-quality/forecast?latitude=${lat}&longitude=${lon}&days=${days}`),

  // Recommendations
  generateActionPlan: (lat: number, lon: number) =>
    request<BreatheSmartActionPlanResponse>(`/api/v1/recommendations/generate?latitude=${lat}&longitude=${lon}`, {
      method: 'POST',
    }),

  getIndoorAdvisor: (lat: number, lon: number, hasPurifier = true) =>
    request<any>(`/api/v1/recommendations/indoor?latitude=${lat}&longitude=${lon}&has_purifier=${hasPurifier}`),

  // Sustainability
  compareCommute: (data: {
    baseline_mode: string;
    alternative_mode: string;
    distance_km: number;
    trips_per_week?: number;
  }) =>
    request<CommuteShiftImpact>('/api/v1/sustainability/compare', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // AI Assistant Chat
  chatWithAssistant: (message: string, lat?: number, lon?: number, history: any[] = []) => {
    const query = lat && lon ? `?latitude=${lat}&longitude=${lon}` : '';
    return request<any>(`/api/v1/assistant/chat${query}`, {
      method: 'POST',
      body: JSON.stringify({ message, history }),
    });
  },

  // Profile
  getProfile: () => request<any>('/api/v1/profile'),
  updateProfile: (profileData: any) =>
    request<any>('/api/v1/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    }),

  // Feedback
  submitFeedback: (recommendationId: string, rating: number, feedback?: string) =>
    request<any>('/api/v1/feedback', {
      method: 'POST',
      body: JSON.stringify({
        recommendation_id: recommendationId,
        rating,
        feedback,
      }),
    }),
};
