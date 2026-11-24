import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LoadingSkeleton } from '../common/LoadingSkeleton'

describe('LoadingSkeleton Component', () => {
  it('renders loading status with aria-live and screen-reader announcement', () => {
    render(<LoadingSkeleton />)
    const status = screen.getByRole('status')
    expect(status).toHaveAttribute('aria-live', 'polite')
    expect(status).toHaveAttribute('aria-label', 'Loading content, please wait')
    expect(screen.getByText('Loading page content')).toHaveClass('sr-only')
  })
})
