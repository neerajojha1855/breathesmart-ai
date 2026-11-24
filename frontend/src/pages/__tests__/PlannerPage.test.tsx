import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { PlannerPage } from '../PlannerPage'
import { LocationProvider } from '../../contexts/LocationContext'

vi.mock('../../services/api', () => ({
  api: {
    generateActionPlan: vi.fn().mockResolvedValue({
      summary: 'High Risk Winter Smog Warning',
      explanation: 'Ground-level temperature inversion trapping high PM2.5 concentrations.',
      safety_notes: ['Avoid high exertion outdoors during severe AQI.'],
      recommendations: [
        {
          id: 'rec-1',
          time_segment: 'morning',
          title: 'Reschedule outdoor morning cardio',
          action: 'Shift outdoor workouts to indoor gym or delay until afternoon boundary layer lifts.',
          priority: 'high',
          category: 'commute_and_activity',
          reason: 'Temperature inversion traps particulate matter close to ground level.',
          expected_impact: 'Reduces PM2.5 inhalation by ~70%',
          impact_type: 'Exposure Reduction',
          confidence: 'high',
          assumptions: [],
        },
        {
          id: 'rec-2',
          time_segment: 'afternoon',
          title: 'Ventilation Flush Window',
          action: 'Open windows for 15-20 minutes between 14:00 and 15:30 to expel built-up indoor CO2.',
          priority: 'medium',
          category: 'indoor_environment',
          reason: 'Solar heating lifts the ground inversion layer in early afternoon.',
          expected_impact: 'Lowers indoor CO2 below 900 ppm without significant PM infiltration.',
          impact_type: 'Indoor Air Quality',
          confidence: 'high',
          assumptions: [],
        },
      ],
    }),
    submitFeedback: vi.fn().mockResolvedValue({}),
  },
}))

function renderPlanner() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <LocationProvider>
        <PlannerPage />
      </LocationProvider>
    </QueryClientProvider>
  )
}

describe('PlannerPage', () => {
  it('renders daily action planner heading and recommendations', async () => {
    renderPlanner()
    expect(screen.getByText('Personalized Daily Action Plan')).toBeInTheDocument()
    expect(await screen.findByText('Reschedule outdoor morning cardio')).toBeInTheDocument()
    expect(screen.getByText('Ventilation Flush Window')).toBeInTheDocument()
  })

  it('displays situation brief and recommendations', async () => {
    renderPlanner()
    expect(await screen.findByText('High Risk Winter Smog Warning')).toBeInTheDocument()
    expect(screen.getByText(/Ground-level temperature inversion/)).toBeInTheDocument()
  })
})
