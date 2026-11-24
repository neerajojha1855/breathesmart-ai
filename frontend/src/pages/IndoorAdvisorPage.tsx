import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, CheckCircle2, Flame, Home, Wind, Zap } from 'lucide-react';
import { useLocation } from '../hooks/useLocation';
import { api } from '../services/api';

export const IndoorAdvisorPage: React.FC = () => {
  const { location } = useLocation();

  const { data: report, isLoading, error } = useQuery({
    queryKey: ['indoorAdvisor', location.latitude, location.longitude],
    queryFn: () => api.getIndoorAdvisor(location.latitude, location.longitude, true),
  });

  const getSuitabilityColor = (s: string) => {
    switch (s?.toLowerCase()) {
      case 'optimal':
        return 'bg-emerald-50 text-emerald-800 border-emerald-300';
      case 'controlled':
        return 'bg-amber-50 text-amber-800 border-amber-300';
      case 'unfavorable':
        return 'bg-orange-50 text-orange-800 border-orange-300';
      default:
        return 'bg-rose-50 text-rose-800 border-rose-300';
    }
  };

  return (
    <div className="space-y-6">
      <div className="pb-2 border-b border-slate-200">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Indoor Air Quality & Ventilation Advisor
        </h1>
        <p className="text-sm text-slate-500">
          Scientifically sound window schedules balancing outdoor smog against dangerous indoor CO2 buildup
        </p>
      </div>

      {isLoading && (
        <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center animate-pulse">
          <Wind className="w-8 h-8 text-emerald-500 animate-spin mx-auto mb-3" />
          <p className="text-sm font-semibold text-slate-700">Evaluating indoor ventilation and filtration safety...</p>
        </div>
      )}

      {error && (
        <div className="bg-rose-50 border border-rose-200 rounded-2xl p-6 text-rose-800 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-bold">Unable to load indoor advisor</h3>
            <p className="text-xs mt-1 text-rose-700">Please check network connectivity.</p>
          </div>
        </div>
      )}

      {report && (
        <div className="space-y-6">
          {/* Real-Time Window Opening Advisor */}
          <div className={`rounded-2xl p-6 border ${getSuitabilityColor(report.ventilation.suitability)}`}>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-3">
              <div className="flex items-center gap-3">
                <Home className="w-6 h-6" />
                <div>
                  <h2 className="text-lg font-bold">Window Opening Verdict: {report.ventilation.suitability.toUpperCase()}</h2>
                  <p className="text-xs opacity-90">{report.ventilation.rationale}</p>
                </div>
              </div>
              <div className="bg-white/80 backdrop-blur-xs px-4 py-2 rounded-xl border border-current self-start sm:self-auto text-center">
                <span className="text-[10px] font-bold uppercase tracking-wider block">Recommended Window</span>
                <span className="text-sm font-black">{report.ventilation.recommended_window}</span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-current/20 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <strong className="block mb-1 font-bold">Action Guidance:</strong>
                <ul className="list-disc list-inside space-y-1">
                  {report.ventilation.action_steps.map((step: string, i: number) => (
                    <li key={i}>{step}</li>
                  ))}
                </ul>
              </div>

              <div className="bg-white/40 p-3 rounded-lg">
                <strong className="block mb-1 font-bold">CO2 Management Warning:</strong>
                <p>{report.ventilation.co2_management_warning}</p>
              </div>
            </div>
          </div>

          {/* Purifier Optimization Card */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs">
            <h3 className="text-base font-bold text-slate-900 mb-2 flex items-center gap-2">
              <Zap className="w-4 h-4 text-emerald-600" /> HEPA Air Purifier Optimization
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                <span className="text-xs text-slate-500 font-medium">Recommended Setting</span>
                <div className="text-base font-bold text-slate-900 mt-1">{report.purification.recommended_mode}</div>
              </div>
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                <span className="text-xs text-slate-500 font-medium">Target Indoor PM2.5</span>
                <div className="text-base font-bold text-emerald-700 mt-1">{report.purification.target_pm25_indoor}</div>
              </div>
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                <span className="text-xs text-slate-500 font-medium">Target Air Changes / Hour</span>
                <div className="text-base font-bold text-slate-900 mt-1">{report.purification.estimated_air_changes_per_hour} ACH</div>
              </div>
            </div>
            <p className="text-xs text-slate-500 mt-4 leading-relaxed">
              <strong>Maintenance: </strong>{report.purification.filter_health_guidance}
            </p>
          </div>

          {/* Cooking & Combustion Safety Checklists */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs">
              <h3 className="text-base font-bold text-slate-900 mb-3 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Kitchen & Cooking Practices
              </h3>
              <ul className="space-y-2 text-xs text-slate-600">
                {report.cooking_safety_checklist.map((item: string, i: number) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0"></span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs">
              <h3 className="text-base font-bold text-slate-900 mb-3 flex items-center gap-2">
                <Flame className="w-4 h-4 text-rose-600" /> Combustion Hazards to Prohibit
              </h3>
              <ul className="space-y-2 text-xs text-slate-600">
                {report.combustion_hazards_to_avoid.map((item: string, i: number) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mt-1.5 shrink-0"></span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
