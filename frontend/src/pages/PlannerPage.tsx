import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { AlertCircle, CheckCircle, Clock, ShieldAlert, Sparkles, ThumbsDown, ThumbsUp, Zap } from 'lucide-react';
import { useLocation } from '../hooks/useLocation';
import { api } from '../services/api';
import type { ActionRecommendationItem } from '../types';

export const PlannerPage: React.FC = () => {
  const { location } = useLocation();
  const [feedbackSent, setFeedbackSent] = useState<Record<string, boolean>>({});

  const { data: plan, isLoading, error, refetch } = useQuery({
    queryKey: ['actionPlan', location.latitude, location.longitude],
    queryFn: () => api.generateActionPlan(location.latitude, location.longitude),
  });

  const handleFeedback = async (recId: string, rating: number) => {
    try {
      await api.submitFeedback(recId, rating);
      setFeedbackSent((prev) => ({ ...prev, [recId]: true }));
    } catch {
      // Graceful fallback
    }
  };

  const priorityColor = (p: string) => {
    switch (p) {
      case 'urgent':
        return 'bg-rose-100 text-rose-800 border-rose-300';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      default:
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Personalized Daily Action Plan
          </h1>
          <p className="text-sm text-slate-500">
            Intelligent routine adjustments for {location.city} based on hourly smog dispersion
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isLoading}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg transition-colors focus-visible:ring-2 focus-visible:ring-emerald-500 self-start sm:self-auto"
        >
          <Sparkles className="w-3.5 h-3.5" />
          Refresh Plan
        </button>
      </div>

      {isLoading && (
        <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center animate-pulse">
          <Zap className="w-8 h-8 text-emerald-500 animate-spin mx-auto mb-3" />
          <p className="text-sm font-semibold text-slate-700">Synthesizing personalized routines with Groq AI...</p>
        </div>
      )}

      {error && (
        <div className="bg-rose-50 border border-rose-200 rounded-2xl p-6 text-rose-800 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-bold">Failed to load recommendations</h3>
            <p className="text-xs mt-1 text-rose-700">Please try refreshing the plan or check your network.</p>
          </div>
        </div>
      )}

      {plan && (
        <>
          {/* Executive Summary Card */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Situation Brief</span>
            </div>
            <p className="text-base font-semibold text-slate-800 leading-relaxed">{plan.summary}</p>
            <p className="text-xs text-slate-500">{plan.explanation}</p>
          </div>

          {/* Action Recommendations Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {plan.recommendations.map((rec: ActionRecommendationItem, index: number) => {
              const recKey = `rec-${index}`;
              const hasGivenFeedback = feedbackSent[recKey];

              return (
                <div key={index} className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between space-y-4">
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <span className={`text-[11px] font-bold uppercase px-2.5 py-0.5 rounded-md border ${priorityColor(rec.priority)}`}>
                        {rec.priority} Priority
                      </span>
                      <div className="flex items-center gap-1 text-xs text-slate-500">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{rec.recommended_time}</span>
                      </div>
                    </div>

                    <h3 className="text-base font-bold text-slate-900">{rec.title}</h3>
                    <p className="text-sm text-slate-700 mt-2 font-medium bg-slate-50 p-3 rounded-xl border border-slate-100">
                      {rec.action}
                    </p>

                    <div className="mt-3 space-y-2 text-xs">
                      <div className="text-slate-600">
                        <strong className="text-slate-800">Scientific Rationale: </strong>
                        {rec.reason}
                      </div>

                      <div className="text-emerald-700 bg-emerald-50/60 p-2 rounded-lg border border-emerald-100">
                        <strong>Expected Impact ({rec.impact_type}): </strong>
                        {rec.expected_impact}
                      </div>

                      {Boolean(rec.assumptions?.length) && (
                        <div className="text-[11px] text-slate-400">
                          <strong>Note: </strong>
                          {rec.assumptions?.join(' ')}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                    <span className="capitalize">Confidence: {rec.confidence}</span>

                    {hasGivenFeedback ? (
                      <span className="text-emerald-600 font-semibold flex items-center gap-1">
                        <CheckCircle className="w-3.5 h-3.5" /> Feedback recorded
                      </span>
                    ) : (
                      <div className="flex items-center gap-2">
                        <span>Helpful?</span>
                        <button
                          onClick={() => handleFeedback(recKey, 5)}
                          className="p-1 rounded hover:bg-slate-100 text-slate-600 hover:text-emerald-600"
                          aria-label="Mark helpful"
                        >
                          <ThumbsUp className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleFeedback(recKey, 1)}
                          className="p-1 rounded hover:bg-slate-100 text-slate-600 hover:text-rose-600"
                          aria-label="Mark unhelpful"
                        >
                          <ThumbsDown className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Safety & Limitations Disclaimers */}
          {Boolean(plan.safety_notes?.length) && (
            <div className="bg-slate-100 rounded-xl p-4 text-xs text-slate-600 flex items-start gap-2.5">
              <ShieldAlert className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
              <div>
                <strong className="text-slate-800">Safety Notes: </strong>
                {plan.safety_notes.join(' • ')}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
