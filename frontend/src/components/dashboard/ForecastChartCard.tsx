import React, { useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Table } from 'lucide-react';

export interface ForecastChartPoint {
  time: string;
  aqi: number;
  pm25: number;
}

interface ForecastChartCardProps {
  chartData: ForecastChartPoint[];
}

export const ForecastChartCard: React.FC<ForecastChartCardProps> = ({ chartData }) => {
  const [showTable, setShowTable] = useState(false);

  return (
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
          <table
            className="w-full text-left text-xs text-slate-600"
            aria-label="Hourly Air Quality Forecast Data"
          >
            <caption className="sr-only">
              Hourly forecast of US AQI and PM2.5 concentrations
            </caption>
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
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '0.75rem',
                  color: '#fff',
                  fontSize: '12px',
                }}
                labelStyle={{ color: '#94a3b8', fontWeight: 600 }}
              />
              <Area
                type="monotone"
                dataKey="aqi"
                name="US AQI"
                stroke="#059669"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#aqiGrad)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};
