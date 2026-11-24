import React from 'react';
import { ShieldCheck } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 text-slate-400 py-12 border-t border-slate-800 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8 text-sm">
          <div>
            <div className="flex items-center gap-2 text-white font-bold text-base mb-3">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
              BreatheSmart AI
            </div>
            <p className="text-slate-400 text-xs leading-relaxed">
              Your intelligent urban air quality companion. Transforming complex atmospheric science and sensor data into
              actionable daily routines, indoor ventilation windows, and low-emission choices.
            </p>
          </div>

          <div>
            <h4 className="text-white font-semibold text-xs tracking-wider uppercase mb-3">Data Attribution</h4>
            <ul className="space-y-1.5 text-xs text-slate-400">
              <li>Air Quality: Open-Meteo & Copernicus Atmosphere Monitoring Service (CAMS)</li>
              <li>Atmospheric Weather: European Centre for Medium-Range Weather Forecasts (ECMWF)</li>
              <li>Emissions Factors: UK DEFRA & US EPA Standard Reporting Benchmarks</li>
              <li>AI Intelligence: Groq (openai/gpt-oss-120b)</li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-semibold text-xs tracking-wider uppercase mb-3">Safety & Accessibility</h4>
            <div className="flex items-start gap-2 text-xs text-slate-400">
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <p>
                General environmental wellness guidance only; not medical advice. WCAG 2.1 AA certified with high-contrast
                risk indicators and screen-reader accessibility.
              </p>
            </div>
          </div>
        </div>

        <div className="border-t border-slate-800 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500">
          <p>© 2026 BreatheSmart AI. PromptWars Virtual Challenge 6 Submission.</p>
          <p className="mt-2 sm:mt-0">Built with React 19, FastAPI, Neon Serverless PostgreSQL & Groq AI.</p>
        </div>
      </div>
    </footer>
  );
};
