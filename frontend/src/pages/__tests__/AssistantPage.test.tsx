import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AssistantPage } from '../AssistantPage'
import { LocationProvider } from '../../contexts/LocationContext'

vi.mock('../../services/api', () => ({
  api: {
    chatWithAssistant: vi.fn().mockResolvedValue({
      message: 'Given current PM2.5 levels, keep outdoor walks brief and wear an N95 mask.',
      context_sources: ['Open-Meteo Air Quality', 'Groq openai/gpt-oss-120b'],
      suggested_followups: ['When will AQI improve?'],
    }),
  },
}))

function renderAssistant() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <LocationProvider>
        <AssistantPage />
      </LocationProvider>
    </QueryClientProvider>
  )
}

describe('AssistantPage', () => {
  it('renders grounded greeting and responds to user questions', async () => {
    const user = userEvent.setup()
    renderAssistant()

    expect(screen.getByText('Conversational AI Assistant')).toBeInTheDocument()
    expect(screen.getByText(/Hello! I am BreatheSmart AI/)).toBeInTheDocument()

    const input = screen.getByLabelText('Ask a question about air quality')
    await user.type(input, 'Should I wear a mask?')
    await user.click(screen.getByLabelText('Send message'))

    expect(await screen.findByText(/Given current PM2\.5 levels/)).toBeInTheDocument()
  })
})
