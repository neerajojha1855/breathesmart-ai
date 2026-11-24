import React from 'react';
import { Wind } from 'lucide-react';

export const LoadingSkeleton: React.FC = () => {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-label="Loading content, please wait"
      className="space-y-6 animate-pulse"
    >
      <div className="h-8 bg-slate-200 rounded-lg w-1/3 mb-2"></div>
      <div className="h-4 bg-slate-200 rounded-lg w-1/2 mb-6"></div>

      <div className="bg-white rounded-2xl p-8 border border-slate-200 flex flex-col items-center justify-center">
        <Wind className="w-8 h-8 text-emerald-500 animate-spin mb-3" aria-hidden="true" />
        <span className="text-xs font-semibold text-slate-500">Loading atmospheric data and recommendations...</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="h-32 bg-slate-200 rounded-xl"></div>
        <div className="h-32 bg-slate-200 rounded-xl"></div>
        <div className="h-32 bg-slate-200 rounded-xl"></div>
      </div>
      <span className="sr-only">Loading page content</span>
    </div>
  );
};
