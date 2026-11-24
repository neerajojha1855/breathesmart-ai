import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { SustainabilityPage } from '../SustainabilityPage'

vi.mock('../../services/api', () => ({
  api: {
    compareCommute: vi.fn().mockResolvedValue({
      baseline_mode: 'petrol_car',
      alternative_mode: 'metro_train',
      distance_km: 15.0,
      trips_per_week: 10,
      weekly_co2e_saved_kg: 24.5,
      annual_co2e_saved_kg: 1274.0,
      exposure_reduction_pct: 65,
      trees_equivalent_annual: 58,
      explanation: 'Taking the electric metro saves ~24.5 kg CO2e weekly while filtered cabins cut particulate exposure by 65%.',
      direct_emissions_benefit: 'Net reduction of 24.5 kg CO2e per week.',
      acute_exposure_benefit: 'Filtered subway cabin reduces particulate exposure.',
      methodology: 'DEFRA 2024 emissions conversion factors.',
      assumptions: ['15 km one-way distance', '10 trips per week'],
    }),
  },
}))

function renderSustainability() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <SustainabilityPage />
    </QueryClientProvider>
  )
}

describe('SustainabilityPage', () => {
  it('renders sustainability calculator heading and inputs', () => {
    renderSustainability()
    expect(screen.getByText('Sustainable Lifestyle & Commute Calculator')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Calculate Environmental Impact/i })).toBeInTheDocument()
  })

  it('calculates and renders DEFRA/EPA emissions savings and acute exposure separation', async () => {
    renderSustainability()
    const calcBtn = screen.getByRole('button', { name: /Calculate Environmental Impact/i })
    fireEvent.click(calcBtn)
    expect(await screen.findByText('24.5 kg')).toBeInTheDocument()
    expect(screen.getByText('58')).toBeInTheDocument()
    expect(screen.getByText(/Net reduction of 24.5 kg CO2e per week/)).toBeInTheDocument()
  })
})
