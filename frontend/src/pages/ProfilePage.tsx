import React, { useEffect, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Check, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';
import type { UserProfile } from '../types';

export const ProfilePage: React.FC = () => {
  const [preferredLanguage, setPreferredLanguage] = useState('en');
  const [housingType, setHousingType] = useState('apartment');
  const [floorLevel, setFloorLevel] = useState('middle');
  const [hasPurifier, setHasPurifier] = useState(true);
  const [primaryCommute, setPrimaryCommute] = useState('metro');
  const [sensitiveGroupConsent, setSensitiveGroupConsent] = useState(false);
  const [hasChildren, setHasChildren] = useState(false);
  const [hasElderly, setHasElderly] = useState(false);
  const [hasRespiratorySensitivities, setHasRespiratorySensitivities] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: api.getProfile,
  });

  useEffect(() => {
    if (profile) {
      setPreferredLanguage(profile.preferred_language || 'en');
      setSensitiveGroupConsent(profile.sensitive_group_consent || false);
      const hp = (profile.household_preferences || {}) as Record<string, unknown>;
      setHousingType((hp.housing_type as string) || 'apartment');
      setFloorLevel((hp.floor_level as string) || 'middle');
      setHasPurifier((hp.has_purifier as boolean) ?? true);
      setHasChildren((hp.has_children as boolean) || false);
      setHasElderly((hp.has_elderly as boolean) || false);
      setHasRespiratorySensitivities((hp.has_respiratory_sensitivities as boolean) || false);
      const cp = (profile.commuting_preferences || {}) as Record<string, unknown>;
      setPrimaryCommute((cp.primary_mode as string) || 'metro');
    }
  }, [profile]);

  const mutation = useMutation({
    mutationFn: (data: Partial<UserProfile>) => api.updateProfile(data),
    onSuccess: () => {
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      preferred_language: preferredLanguage,
      sensitive_group_consent: sensitiveGroupConsent,
      household_preferences: {
        housing_type: housingType,
        floor_level: floorLevel,
        has_purifier: hasPurifier,
        has_children: sensitiveGroupConsent ? hasChildren : false,
        has_elderly: sensitiveGroupConsent ? hasElderly : false,
        has_respiratory_sensitivities: sensitiveGroupConsent ? hasRespiratorySensitivities : false,
      },
      commuting_preferences: {
        primary_mode: primaryCommute,
      },
      indoor_environment_preferences: {
        has_purifier: hasPurifier,
      },
    });
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="pb-2 border-b border-slate-200">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Household & Living Preferences
        </h1>
        <p className="text-sm text-slate-500">
          Personalize air quality alerts, ventilation schedules, and daily action plans
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-5">
        <div>
          <label htmlFor="pref-lang" className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
            Preferred Language
          </label>
          <select
            id="pref-lang"
            value={preferredLanguage}
            onChange={(e) => setPreferredLanguage(e.target.value)}
            className="w-full text-sm rounded-lg border border-slate-300 p-2 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
          >
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="es">Spanish</option>
          </select>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="housing-type" className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              Housing Structure
            </label>
            <select
              id="housing-type"
              value={housingType}
              onChange={(e) => setHousingType(e.target.value)}
              className="w-full text-sm rounded-lg border border-slate-300 p-2 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
            >
              <option value="apartment">Multi-story Apartment</option>
              <option value="independent_house">Independent House / Villa</option>
              <option value="row_house">Townhouse / Row House</option>
            </select>
          </div>

          <div>
            <label htmlFor="floor-level" className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              Floor Level
            </label>
            <select
              id="floor-level"
              value={floorLevel}
              onChange={(e) => setFloorLevel(e.target.value)}
              className="w-full text-sm rounded-lg border border-slate-300 p-2 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
            >
              <option value="ground">Ground Floor (Higher Road Dust)</option>
              <option value="middle">Middle Floor (3rd - 8th)</option>
              <option value="high">High Floor (9th+ Above Ground Inversion)</option>
            </select>
          </div>
        </div>

        <div>
          <label htmlFor="primary-commute" className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
            Typical Commuting Mode
          </label>
          <select
            id="primary-commute"
            value={primaryCommute}
            onChange={(e) => setPrimaryCommute(e.target.value)}
            className="w-full text-sm rounded-lg border border-slate-300 p-2 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
          >
            <option value="metro">Metro / Subway</option>
            <option value="car">Private Car</option>
            <option value="bus">Public Bus</option>
            <option value="two_wheeler">Motorcycle / Scooter</option>
            <option value="cycling">Bicycle</option>
            <option value="walking">Walking</option>
          </select>
        </div>

        <div className="flex items-center gap-3 pt-2">
          <input
            id="has-purifier"
            type="checkbox"
            checked={hasPurifier}
            onChange={(e) => setHasPurifier(e.target.checked)}
            className="w-4 h-4 accent-emerald-600 rounded"
          />
          <label htmlFor="has-purifier" className="text-sm font-semibold text-slate-800">
            Household possesses a HEPA air purifier
          </label>
        </div>

        {/* Sensitive Groups & Privacy Consent */}
        <div className="pt-4 border-t border-slate-100 space-y-3">
          <div className="flex items-start gap-2.5">
            <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-bold text-slate-900">Sensitive Group Considerations</h3>
              <p className="text-xs text-slate-500">
                Optional: Tailor recommendations for household members vulnerable to particulate smog.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 bg-slate-50 p-3 rounded-xl border border-slate-200">
            <input
              id="sensitive-consent"
              type="checkbox"
              checked={sensitiveGroupConsent}
              onChange={(e) => setSensitiveGroupConsent(e.target.checked)}
              className="w-4 h-4 accent-emerald-600 rounded"
            />
            <label htmlFor="sensitive-consent" className="text-xs font-medium text-slate-700">
              I consent to having my household recommendations account for sensitive groups (no medical details required).
            </label>
          </div>

          {sensitiveGroupConsent && (
            <div className="space-y-2 pl-4 border-l-2 border-emerald-500 text-xs text-slate-700">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={hasChildren}
                  onChange={(e) => setHasChildren(e.target.checked)}
                  className="accent-emerald-600 rounded"
                />
                Children under 14 years
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={hasElderly}
                  onChange={(e) => setHasElderly(e.target.checked)}
                  className="accent-emerald-600 rounded"
                />
                Older adults (65+)
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={hasRespiratorySensitivities}
                  onChange={(e) => setHasRespiratorySensitivities(e.target.checked)}
                  className="accent-emerald-600 rounded"
                />
                Respiratory or cardiovascular sensitivities (asthma, bronchitis)
              </label>
            </div>
          )}
        </div>

        <div className="pt-4 flex items-center justify-between">
          <button
            type="submit"
            disabled={mutation.isPending}
            className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg transition-colors focus-visible:ring-2 focus-visible:ring-emerald-500"
          >
            {mutation.isPending ? 'Saving...' : 'Save Preferences'}
          </button>

          {savedSuccess && (
            <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
              <Check className="w-4 h-4" /> Preferences saved!
            </span>
          )}
        </div>
      </form>
    </div>
  );
};
