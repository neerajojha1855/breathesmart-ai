import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { DashboardPage } from '../DashboardPage'
import { LocationProvider } from '../../contexts/LocationContext'
import { MemoryRouter } from 'react-router-dom'

vi.mock('../../services/api', () => ({
  api: {
    getCurrentAirQuality: vi.fn().mockResolvedValue({
      aqi: 165,
      aqi_category: 'unhealthy',
      dominant_pollutant: 'pm2_5',
      pollutants: {
        pm2_5: { value: 85.4, unit: 'µg/m³' },
        pm10: { value: 142.1, unit: 'µg/m³' },
        no2: { value: 45.2, unit: 'µg/m³' },
        o3: { value: 32.0, unit: 'µg/m³' },
        so2: { value: 12.8, unit: 'µg/m³' },
        co: { value: 1.8, unit: 'mg/m³' },
      },
      source_metadata: { provider: 'Open-Meteo', data_type: 'modeled' },
    }),
    getAirQualityForecast: vi.fn().mockResolvedValue({
      hourly: [
        { timestamp: '2026-11-24T00:00:00Z', aqi: 150, pm2_5: 75 },
        { timestamp: '2026-11-24T06:00:00Z', aqi: 180, pm2_5: 95 },
      ],
    }),
  },
}))

function renderDashboard() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <LocationProvider>
          <DashboardPage />
        </LocationProvider>
      </QueryClientProvider>
    </MemoryRouter>
  )
}

describe('DashboardPage', () => {
  it('renders dashboard heading for active city', async () => {
    renderDashboard()
    expect(await screen.findByText(/Air Quality in New Delhi/)).toBeInTheDocument()
  })

  it('renders live AQI hero card when data loads', async () => {
    renderDashboard()
    expect(await screen.findByText('165')).toBeInTheDocument()
    expect(screen.getByText('Unhealthy')).toBeInTheDocument()
  })

  it('renders multi-pollutant breakdown cards', async () => {
    renderDashboard()
    expect(await screen.findByText('PM2.5')).toBeInTheDocument()
    expect(screen.getByText('PM10')).toBeInTheDocument()
    expect(screen.getByText('NO2')).toBeInTheDocument()
    expect(screen.getByText('O3')).toBeInTheDocument()
  })

  it('supports toggling table view for screen readers', async () => {
    renderDashboard()
    const toggleBtn = await screen.findByRole('button', { name: /View Accessible Table/i })
    expect(toggleBtn).toBeInTheDocument()
    fireEvent.click(toggleBtn)
    expect(screen.getByRole('table')).toBeInTheDocument()
  })
})
