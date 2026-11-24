import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { IndoorAdvisorPage } from '../IndoorAdvisorPage'
import { LocationProvider } from '../../contexts/LocationContext'

vi.mock('../../services/api', () => ({
  api: {
    getIndoorAdvisor: vi.fn().mockResolvedValue({
      ventilation: {
        suitability: 'controlled',
        can_open_windows: true,
        recommended_window: '01:00 PM - 02:30 PM',
        max_duration_minutes: 25,
        rationale: 'Afternoon solar mixing temporarily disperses surface particulate matter.',
        co2_management_warning: 'Keep cross-ventilation brief to prevent CO2 buildup above 1000 ppm.',
        action_steps: ['Open opposite-facing windows for 20 minutes.', 'Resume HEPA filtration immediately after closing.'],
      },
      purification: {
        has_purifier: true,
        recommended_mode: 'High / Turbo Mode (Continuous)',
        filter_health_guidance: 'Inspect pre-filter mesh bi-weekly.',
        target_pm25_indoor: '< 15 µg/m³',
        estimated_air_changes_per_hour: 5.0,
      },
      cooking_safety_checklist: ['Activate range hood exhaust before turning on gas stoves.'],
      combustion_hazards_to_avoid: ['Avoid burning incense or candles indoors during smog episodes.'],
    }),
  },
}))

function renderIndoorAdvisor() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <LocationProvider>
        <IndoorAdvisorPage />
      </LocationProvider>
    </QueryClientProvider>
  )
}

describe('IndoorAdvisorPage', () => {
  it('renders ventilation verdict, purifier settings, and safety checklists', async () => {
    renderIndoorAdvisor()
    expect(screen.getByText('Indoor Air Quality & Ventilation Advisor')).toBeInTheDocument()
    expect(await screen.findByText(/Window Opening Verdict: CONTROLLED/)).toBeInTheDocument()
    expect(screen.getByText('01:00 PM - 02:30 PM')).toBeInTheDocument()
    expect(screen.getByText('High / Turbo Mode (Continuous)')).toBeInTheDocument()
    expect(screen.getByText('5 ACH')).toBeInTheDocument()
    expect(screen.getByText(/Activate range hood exhaust/)).toBeInTheDocument()
    expect(screen.getByText(/Avoid burning incense or candles/)).toBeInTheDocument()
  })
})
