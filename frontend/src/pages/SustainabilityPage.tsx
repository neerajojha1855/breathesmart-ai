import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Leaf, ShieldCheck, Trees } from 'lucide-react';
import { api } from '../services/api';
import type { CommuteShiftImpact } from '../types';

export const SustainabilityPage: React.FC = () => {
  const [baseline, setBaseline] = useState('petrol_car');
  const [alternative, setAlternative] = useState('metro_train');
  const [distance, setDistance] = useState(15);
  const [tripsPerWeek, setTripsPerWeek] = useState(10);
  const [impactResult, setImpactResult] = useState<CommuteShiftImpact | null>(null);

  const mutation = useMutation({
    mutationFn: api.compareCommute,
    onSuccess: (data) => {
      setImpactResult(data);
    },
  });

  const handleCalculate = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      baseline_mode: baseline,
      alternative_mode: alternative,
      distance_km: distance,
      trips_per_week: tripsPerWeek,
    });
  };

  const transportOptions = [
    { id: 'petrol_car', label: 'Petrol Car (Solo)' },
    { id: 'diesel_car', label: 'Diesel Car (Solo)' },
    { id: 'electric_car', label: 'Electric Car (EV)' },
    { id: 'motorcycle', label: 'Motorcycle / Scooter' },
    { id: 'metro_train', label: 'Metro / Urban Train' },
    { id: 'city_bus', label: 'Public City Bus' },
    { id: 'cycling', label: 'Bicycle / E-Bike' },
    { id: 'walking', label: 'Walking' },
  ];

  return (
    <div className="space-y-6">
      <div className="pb-2 border-b border-slate-200">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Sustainable Lifestyle & Commute Calculator
        </h1>
        <p className="text-sm text-slate-500">
          Quantified emission reductions with verified DEFRA/EPA factors and personal particulate exposure separation
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form Controls */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs lg:col-span-1">
          <form onSubmit={handleCalculate} className="space-y-4">
            <div>
              <label htmlFor="baseline-mode" className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
                Current Commute Mode
              </label>
              <select
                id="baseline-mode"
                value={baseline}
                onChange={(e) => setBaseline(e.target.value)}
                className="w-full text-sm rounded-lg border border-slate-300 p-2 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
              >
                {transportOptions.map((opt) => (
                  <option key={opt.id} value={opt.id}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="alt-mode" className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
                Low-Emission Alternative
              </label>
              <select
                id="alt-mode"
                value={alternative}
                onChange={(e) => setAlternative(e.target.value)}
                className="w-full text-sm rounded-lg border border-slate-300 p-2 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
              >
                {transportOptions.map((opt) => (
                  <option key={opt.id} value={opt.id}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold text-slate-700 mb-1">
                <label htmlFor="distance-slider">One-Way Distance</label>
                <span>{distance} km</span>
              </div>
              <input
                id="distance-slider"
                type="range"
                min="1"
                max="50"
                value={distance}
                onChange={(e) => setDistance(Number(e.target.value))}
                className="w-full accent-emerald-600"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold text-slate-700 mb-1">
                <label htmlFor="trips-slider">Trips Per Week (e.g. 5 round trips = 10)</label>
                <span>{tripsPerWeek} trips</span>
              </div>
              <input
                id="trips-slider"
                type="range"
                min="1"
                max="20"
                value={tripsPerWeek}
                onChange={(e) => setTripsPerWeek(Number(e.target.value))}
                className="w-full accent-emerald-600"
              />
            </div>

            <button
              type="submit"
              disabled={mutation.isPending}
              className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg transition-colors focus-visible:ring-2 focus-visible:ring-emerald-500"
            >
              {mutation.isPending ? 'Calculating...' : 'Calculate Environmental Impact'}
            </button>
          </form>
        </div>

        {/* Results & Exposure Distinction Display */}
        <div className="lg:col-span-2 space-y-4">
          {impactResult ? (
            <>
              {/* Highlight Metrics */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-5 text-center">
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-800">Weekly CO2e Saved</span>
                  <div className="text-3xl font-black text-emerald-900 mt-1">{impactResult.weekly_co2e_saved_kg} kg</div>
                  <span className="text-[11px] text-emerald-700 mt-1 block">Annual: {impactResult.annual_co2e_saved_kg} kg</span>
                </div>

                <div className="bg-teal-50 border border-teal-200 rounded-2xl p-5 text-center">
                  <span className="text-xs font-bold uppercase tracking-wider text-teal-800">Trees Equivalent</span>
                  <div className="text-3xl font-black text-teal-900 mt-1 flex items-center justify-center gap-1.5">
                    <Trees className="w-6 h-6 text-teal-600" />
                    <span>{impactResult.trees_equivalent_annual}</span>
                  </div>
                  <span className="text-[11px] text-teal-700 mt-1 block">Mature trees absorbing CO2/yr</span>
                </div>

                <div className="bg-slate-900 text-white rounded-2xl p-5 text-center flex flex-col justify-center">
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">Mode Shift Delta</span>
                  <div className="text-xl font-bold mt-1 capitalize">
                    {impactResult.baseline_mode.replace('_', ' ')} → {impactResult.alternative_mode.replace('_', ' ')}
                  </div>
                  <span className="text-[11px] text-slate-400 mt-1 block">
                    {distance * tripsPerWeek} km total / week
                  </span>
                </div>
              </div>

              {/* Crucial Problem Statement Distinction: Exposure vs Emissions */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-4">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-emerald-600" /> Personal Particulate Exposure Benefit
                  </h3>
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
                    {impactResult.particulate_exposure_benefit}
                  </p>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                    <Leaf className="w-4 h-4 text-emerald-600" /> Direct Environmental Emission Benefit
                  </h3>
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
                    {impactResult.direct_emissions_benefit}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-400">
                  <strong className="text-slate-600">Methodology & Assumptions: </strong>
                  {impactResult.methodology}
                  <ul className="list-disc list-inside mt-1 space-y-0.5">
                    {impactResult.assumptions.map((a, i) => (
                      <li key={i}>{a}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center flex flex-col items-center justify-center">
              <Leaf className="w-12 h-12 text-emerald-500 mb-3" />
              <h3 className="text-base font-bold text-slate-900">Quantify Your Sustainable Travel Impact</h3>
              <p className="text-xs text-slate-500 max-w-md mt-1">
                Select your current vehicle and alternative low-emission mode on the left to see verified CO2e savings
                and personal particulate exposure distinctions.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
