import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { NavLink } from 'react-router-dom';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, AlertTriangle, ArrowRight, Clock, Database, Home, Leaf, Table, Wind } from 'lucide-react';
import { useLocation } from '../contexts/LocationContext';
import { api } from '../services/api';
import { getAQIStyle } from '../utils/aqiColors';

export const DashboardPage: React.FC = () => {
  const { location } = useLocation();
  const [showTable, setShowTable] = useState(false);

  const { data: aqi, isLoading: aqiLoading, error: aqiError } = useQuery({
    queryKey: ['airQuality', location.latitude, location.longitude],
    queryFn: () => api.getCurrentAirQuality(location.latitude, location.longitude),
  });

  const { data: forecast } = useQuery({
    queryKey: ['forecast', location.latitude, location.longitude],
    queryFn: () => api.getAirQualityForecast(location.latitude, location.longitude, 2),
  });

  const style = aqi ? getAQIStyle(aqi.aqi_category) : getAQIStyle('unknown');

  const chartData = forecast?.hourly.slice(0, 24).map((pt) => ({
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

          {/* Pollutants Breakdown Grid */}
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-3">Key Atmospheric Pollutants</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {[
                { name: 'PM2.5', label: 'Fine Particulates', val: aqi.pollutants.pm2_5?.value, unit: 'µg/m³', limit: 15 },
                { name: 'PM10', label: 'Coarse Dust', val: aqi.pollutants.pm10?.value, unit: 'µg/m³', limit: 45 },
                { name: 'NO2', label: 'Nitrogen Dioxide', val: aqi.pollutants.no2?.value, unit: 'µg/m³', limit: 25 },
                { name: 'O3', label: 'Ground Ozone', val: aqi.pollutants.o3?.value, unit: 'µg/m³', limit: 100 },
                { name: 'SO2', label: 'Sulfur Dioxide', val: aqi.pollutants.so2?.value, unit: 'µg/m³', limit: 40 },
                { name: 'CO', label: 'Carbon Monoxide', val: aqi.pollutants.co?.value, unit: 'µg/m³', limit: 4000 },
              ].map((p) => {
                const isElevated = p.val !== undefined && p.val > p.limit;
                return (
                  <div key={p.name} className="bg-white rounded-xl p-3.5 border border-slate-200 shadow-xs flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-sm text-slate-800">{p.name}</span>
                        {isElevated && <span className="w-2 h-2 rounded-full bg-amber-500" title="Exceeds WHO 24h Guideline"></span>}
                      </div>
                      <div className="text-[11px] text-slate-400 truncate">{p.label}</div>
                    </div>
                    <div className="mt-2 flex items-baseline gap-1">
                      <span className="text-xl font-extrabold text-slate-900">{p.val !== undefined ? p.val.toFixed(1) : 'N/A'}</span>
                      <span className="text-[10px] text-slate-500">{p.unit}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 24-Hour Trend Chart with Screen-Reader Accessible Alternative */}
          <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-900">24-Hour Pollution Trend</h3>
                <p className="text-xs text-slate-500">Hourly US AQI and PM2.5 forecast curve</p>
              </div>
              <button
                onClick={() => setShowTable(!showTable)}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors focus-visible:ring-2 focus-visible:ring-emerald-500"
                aria-expanded={showTable}
              >
                <Table className="w-3.5 h-3.5" />
                {showTable ? 'View Chart' : 'View Accessible Table'}
              </button>
            </div>

            {showTable ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-600" aria-label="Hourly Air Quality Forecast Data">
                  <caption className="sr-only">Hourly forecast of US AQI and PM2.5 concentrations</caption>
                  <thead className="bg-slate-50 text-slate-800 border-b border-slate-200">
                    <tr>
                      <th className="py-2 px-3">Hour</th>
                      <th className="py-2 px-3">US AQI</th>
                      <th className="py-2 px-3">PM2.5 (µg/m³)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {chartData.map((d, i) => (
                      <tr key={i} className="hover:bg-slate-50">
                        <td className="py-1.5 px-3 font-medium text-slate-700">{d.time}</td>
                        <td className="py-1.5 px-3">{d.aqi}</td>
                        <td className="py-1.5 px-3">{d.pm25.toFixed(1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="h-64 w-full" aria-hidden="true">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="aqiGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="time" tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
                    <YAxis tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', color: '#fff', fontSize: '12px' }}
                      labelStyle={{ color: '#94a3b8', fontWeight: 600 }}
                    />
                    <Area type="monotone" dataKey="aqi" name="US AQI" stroke="#059669" strokeWidth={2.5} fillOpacity={1} fill="url(#aqiGrad)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

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
