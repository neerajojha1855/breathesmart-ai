import React from 'react';
import { ShieldCheck } from 'lucide-react';

interface SensitiveGroupSectionProps {
  sensitiveGroupConsent: boolean;
  onConsentChange: (val: boolean) => void;
  hasChildren: boolean;
  onChildrenChange: (val: boolean) => void;
  hasElderly: boolean;
  onElderlyChange: (val: boolean) => void;
  hasRespiratorySensitivities: boolean;
  onRespiratoryChange: (val: boolean) => void;
}

export const SensitiveGroupSection: React.FC<SensitiveGroupSectionProps> = ({
  sensitiveGroupConsent,
  onConsentChange,
  hasChildren,
  onChildrenChange,
  hasElderly,
  onElderlyChange,
  hasRespiratorySensitivities,
  onRespiratoryChange,
}) => {
  return (
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
          onChange={(e) => onConsentChange(e.target.checked)}
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
              onChange={(e) => onChildrenChange(e.target.checked)}
              className="accent-emerald-600 rounded"
            />
            Children under 14 years
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={hasElderly}
              onChange={(e) => onElderlyChange(e.target.checked)}
              className="accent-emerald-600 rounded"
            />
            Older adults (65+)
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={hasRespiratorySensitivities}
              onChange={(e) => onRespiratoryChange(e.target.checked)}
              className="accent-emerald-600 rounded"
            />
            Respiratory or cardiovascular sensitivities (asthma, bronchitis)
          </label>
        </div>
      )}
    </div>
  );
};
