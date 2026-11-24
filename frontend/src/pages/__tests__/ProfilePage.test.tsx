import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ProfilePage } from '../ProfilePage'

vi.mock('../../services/api', () => ({
  api: {
    getProfile: vi.fn().mockResolvedValue({
      id: 'prof-1',
      session_id: 'sess-1',
      preferred_language: 'en',
      sensitive_group_consent: false,
      household_preferences: {
        housing_type: 'apartment',
        floor_level: 'middle',
        has_purifier: true,
      },
      commuting_preferences: {
        primary_mode: 'metro',
      },
      indoor_environment_preferences: {
        has_purifier: true,
      },
    }),
    updateProfile: vi.fn().mockResolvedValue({}),
  },
}))

function renderProfile() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <ProfilePage />
    </QueryClientProvider>
  )
}

describe('ProfilePage', () => {
  it('renders profile preferences and saves updated settings', async () => {
    const user = userEvent.setup()
    renderProfile()

    expect(screen.getByText('Household & Living Preferences')).toBeInTheDocument()
    const saveButton = await screen.findByRole('button', { name: /Save Preferences/i })
    await user.click(saveButton)

    expect(await screen.findByText(/Preferences saved/i)).toBeInTheDocument()
  })
})
