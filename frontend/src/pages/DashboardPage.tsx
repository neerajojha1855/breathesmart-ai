import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { NavLink } from 'react-router-dom';
import { Activity, AlertTriangle, ArrowRight, Clock, Database, Home, Leaf, Wind } from 'lucide-react';
import { ForecastChartCard } from '../components/dashboard/ForecastChartCard';
import { PollutantGrid } from '../components/dashboard/PollutantGrid';
import { useLocation } from '../hooks/useLocation';
import { api } from '../services/api';
import { getAQIStyle } from '../utils/aqiColors';

export const DashboardPage: React.FC = () => {
  const { location } = useLocation();

  const { data: aqi, isLoading: aqiLoading, error: aqiError } = useQuery({
    queryKey: ['airQuality', location.latitude, location.longitude],
    queryFn: () => api.getCurrentAirQuality(location.latitude, location.longitude),
  });

  const { data: forecast } = useQuery({
    queryKey: ['forecast', location.latitude, location.longitude],
    queryFn: () => api.getAirQualityForecast(location.latitude, location.longitude, 2),
  });

  const style = aqi ? getAQIStyle(aqi.aqi_category) : getAQIStyle('unknown');

  const chartData =
    forecast?.hourly.slice(0, 24).map((pt) => ({
      time: new Date(pt.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      aqi: pt.aqi,
      pm25: pt.pm2_5,
    })) || [];

  return (
    <div className="space-y-6">
      {/* Header Greeting & Location */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Air Quality in {location.city}
          </h1>
          <p className="text-sm text-slate-500">
            Real-time atmospheric diagnostics and personalized urban living recommendations
          </p>
        </div>
        {aqi && (
          <div className="flex items-center gap-2 text-xs text-slate-500 bg-white px-3 py-1.5 rounded-full border border-slate-200 self-start sm:self-auto">
            <Database className="w-3.5 h-3.5 text-emerald-600" />
            <span>{aqi.source_metadata.provider}</span>
            <span>•</span>
            <span className="capitalize">{aqi.source_metadata.data_type}</span>
          </div>
        )}
      </div>

      {aqiLoading && (
        <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center animate-pulse">
          <Wind className="w-8 h-8 text-emerald-500 animate-spin mx-auto mb-3" />
          <p className="text-sm font-medium text-slate-600">Retrieving live atmospheric sensor feeds...</p>
        </div>
      )}

      {aqiError && (
        <div className="bg-rose-50 border border-rose-200 rounded-2xl p-6 text-rose-800 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-bold">Unable to fetch air quality data</h3>
            <p className="text-xs mt-1 text-rose-700">Please verify your internet connection or select another city.</p>
          </div>
        </div>
      )}

      {aqi && (
        <>
          {/* Hero AQI Card */}
          <div className={`rounded-2xl p-6 border ${style.bg} ${style.border} transition-all`}>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div className="flex items-center gap-6">
                <div className="flex flex-col">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Air Quality Index</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-5xl sm:text-6xl font-black text-slate-900">{aqi.aqi}</span>
                    <span className="text-xs font-semibold text-slate-500">{aqi.aqi_standard}</span>
                  </div>
                </div>

                <div className="h-12 w-px bg-slate-300 hidden sm:block"></div>

                <div>
                  <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold ${style.badgeBg} mb-1.5`}>
                    {style.label}
                  </span>
                  <p className="text-xs font-medium text-slate-700 max-w-md">{style.description}</p>
                </div>
              </div>

              <div className="flex flex-col sm:items-end gap-1 text-xs text-slate-500 border-t md:border-t-0 pt-3 md:pt-0 border-slate-200">
                <div className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Updated: {new Date(aqi.source_metadata.observed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                <span>Resolution: {aqi.source_metadata.source_resolution}</span>
              </div>
            </div>
          </div>

          <PollutantGrid pollutants={aqi.pollutants} />

          <ForecastChartCard chartData={chartData} />

          {/* Quick Action Navigation Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <NavLink
              to="/planner"
              className="bg-white rounded-xl p-5 border border-slate-200 hover:border-emerald-300 hover:shadow-md transition-all group flex flex-col justify-between"
            >
              <div>
                <div className="w-9 h-9 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center mb-3">
                  <Activity className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-slate-900 group-hover:text-emerald-700 transition-colors">Personalized Daily Plan</h3>
                <p className="text-xs text-slate-500 mt-1">Time-segmented morning, afternoon, evening, and night actions.</p>
              </div>
              <div className="mt-4 flex items-center text-xs font-semibold text-emerald-600">
                View Recommendations <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition-transform" />
              </div>
            </NavLink>

            <NavLink
              to="/indoor"
              className="bg-white rounded-xl p-5 border border-slate-200 hover:border-emerald-300 hover:shadow-md transition-all group flex flex-col justify-between"
            >
              <div>
                <div className="w-9 h-9 rounded-lg bg-cyan-50 text-cyan-600 flex items-center justify-center mb-3">
                  <Home className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-slate-900 group-hover:text-cyan-700 transition-colors">Indoor Air & Ventilation</h3>
                <p className="text-xs text-slate-500 mt-1">Safe window opening windows and HEPA purifier guidance.</p>
              </div>
              <div className="mt-4 flex items-center text-xs font-semibold text-cyan-600">
                Check Ventilation <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition-transform" />
              </div>
            </NavLink>

            <NavLink
              to="/sustainability"
              className="bg-white rounded-xl p-5 border border-slate-200 hover:border-emerald-300 hover:shadow-md transition-all group flex flex-col justify-between"
            >
              <div>
                <div className="w-9 h-9 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center mb-3">
                  <Leaf className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-slate-900 group-hover:text-teal-700 transition-colors">Low-Emission Commute</h3>
                <p className="text-xs text-slate-500 mt-1">Quantified CO2e and personal particulate exposure comparison.</p>
              </div>
              <div className="mt-4 flex items-center text-xs font-semibold text-teal-600">
                Compare Modes <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition-transform" />
              </div>
            </NavLink>
          </div>
        </>
      )}
    </div>
  );
};
