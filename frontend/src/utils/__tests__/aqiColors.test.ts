import { describe, it, expect } from 'vitest'
import { getAQIStyle } from '../aqiColors'

describe('aqiColors utility', () => {
  it('correctly maps Good category', () => {
    const style = getAQIStyle('Good')
    expect(style.label).toBe('Good')
    expect(style.text).toBe('text-emerald-800')
    expect(style.badgeBg).toBe('bg-emerald-600 text-white')
  })

  it('correctly maps Moderate category', () => {
    const style = getAQIStyle('Moderate')
    expect(style.label).toBe('Moderate')
    expect(style.text).toBe('text-amber-800')
  })

  it('correctly maps Unhealthy for Sensitive Groups', () => {
    const style = getAQIStyle('unhealthy_for_sensitive_groups')
    expect(style.label).toBe('Unhealthy for Sensitive Groups')
  })

  it('correctly maps Unhealthy category', () => {
    const style = getAQIStyle('Unhealthy')
    expect(style.label).toBe('Unhealthy')
  })

  it('correctly maps Very Unhealthy category', () => {
    const style = getAQIStyle('very_unhealthy')
    expect(style.label).toBe('Very Unhealthy')
  })

  it('correctly maps Hazardous category', () => {
    const style = getAQIStyle('Hazardous')
    expect(style.label).toBe('Hazardous')
  })
})
