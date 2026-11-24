import type { AQICategory } from '../types';

export interface AQIStyle {
  label: string;
  bg: string;
  text: string;
  border: string;
  badgeBg: string;
  description: string;
}

export function getAQIStyle(category: AQICategory | string): AQIStyle {
  switch (category?.toLowerCase()) {
    case 'good':
      return {
        label: 'Good',
        bg: 'bg-emerald-50',
        text: 'text-emerald-800',
        border: 'border-emerald-200',
        badgeBg: 'bg-emerald-600 text-white',
        description: 'Air quality is satisfactory and poses little or no risk.',
      };
    case 'moderate':
      return {
        label: 'Moderate',
        bg: 'bg-amber-50',
        text: 'text-amber-800',
        border: 'border-amber-200',
        badgeBg: 'bg-amber-500 text-slate-900 font-bold',
        description: 'Acceptable air quality; sensitive groups should consider reducing prolonged outdoor exertion.',
      };
    case 'unhealthy_for_sensitive_groups':
      return {
        label: 'Unhealthy for Sensitive Groups',
        bg: 'bg-orange-50',
        text: 'text-orange-900',
        border: 'border-orange-200',
        badgeBg: 'bg-orange-500 text-white',
        description: 'Members of sensitive groups may experience health effects. General public less likely affected.',
      };
    case 'unhealthy':
      return {
        label: 'Unhealthy',
        bg: 'bg-rose-50',
        text: 'text-rose-900',
        border: 'border-rose-200',
        badgeBg: 'bg-rose-600 text-white',
        description: 'Some members of the general public may experience health effects; sensitive groups more seriously.',
      };
    case 'very_unhealthy':
      return {
        label: 'Very Unhealthy',
        bg: 'bg-purple-50',
        text: 'text-purple-900',
        border: 'border-purple-200',
        badgeBg: 'bg-purple-700 text-white',
        description: 'Health alert: The risk of health effects is increased for everyone.',
      };
    case 'hazardous':
      return {
        label: 'Hazardous',
        bg: 'bg-red-100',
        text: 'text-red-950',
        border: 'border-red-300',
        badgeBg: 'bg-red-900 text-white',
        description: 'Health warning of emergency conditions: Everyone is more likely to be affected.',
      };
    default:
      return {
        label: 'Unknown',
        bg: 'bg-slate-50',
        text: 'text-slate-700',
        border: 'border-slate-200',
        badgeBg: 'bg-slate-500 text-white',
        description: 'Air quality data currently unavailable or estimating.',
      };
  }
}
