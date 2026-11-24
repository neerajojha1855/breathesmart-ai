import React from 'react';
import type { Pollutants } from '../../types';

interface PollutantGridProps {
  pollutants: Pollutants;
}

interface PollutantSpec {
  name: string;
  label: string;
  val: number | undefined;
  unit: string;
  limit: number;
}

export const PollutantGrid: React.FC<PollutantGridProps> = ({ pollutants }) => {
  const items: PollutantSpec[] = [
    { name: 'PM2.5', label: 'Fine Particulates', val: pollutants.pm2_5?.value, unit: 'µg/m³', limit: 15 },
    { name: 'PM10', label: 'Coarse Dust', val: pollutants.pm10?.value, unit: 'µg/m³', limit: 45 },
    { name: 'NO2', label: 'Nitrogen Dioxide', val: pollutants.no2?.value, unit: 'µg/m³', limit: 25 },
    { name: 'O3', label: 'Ground Ozone', val: pollutants.o3?.value, unit: 'µg/m³', limit: 100 },
    { name: 'SO2', label: 'Sulfur Dioxide', val: pollutants.so2?.value, unit: 'µg/m³', limit: 40 },
    { name: 'CO', label: 'Carbon Monoxide', val: pollutants.co?.value, unit: 'µg/m³', limit: 4000 },
  ];

  return (
    <div>
      <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-3">
        Key Atmospheric Pollutants
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {items.map((p) => {
          const isElevated = p.val !== undefined && p.val > p.limit;
          return (
            <div
              key={p.name}
              className="bg-white rounded-xl p-3.5 border border-slate-200 shadow-xs flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-sm text-slate-800">{p.name}</span>
                  {isElevated && (
                    <span
                      className="w-2 h-2 rounded-full bg-amber-500"
                      title="Exceeds WHO 24h Guideline"
                    />
                  )}
                </div>
                <div className="text-[11px] text-slate-400 truncate">{p.label}</div>
              </div>
              <div className="mt-2 flex items-baseline gap-1">
                <span className="text-xl font-extrabold text-slate-900">
                  {p.val !== undefined ? p.val.toFixed(1) : 'N/A'}
                </span>
                <span className="text-[10px] text-slate-500">{p.unit}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
