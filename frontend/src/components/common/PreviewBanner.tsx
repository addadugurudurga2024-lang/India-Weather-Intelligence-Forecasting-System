import React from 'react';
import { AlertCircle, Terminal } from 'lucide-react';

interface PreviewBannerProps {
  message?: string;
  subtext?: string;
}

export const PreviewBanner: React.FC<PreviewBannerProps> = ({
  message = 'Operational Intelligence • Phase 11 Hardened Architecture',
  subtext = 'FastAPI backend integrated with authoritative Parquet historical telemetry, frozen XGBoost multi-horizon models, and genuine empirical uncertainty intervals.'
}) => {
  return (
    <div style={{
      background: 'color-mix(in srgb, var(--accent-primary) 10%, var(--bg-surface))',
      border: '1px solid var(--border-base)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--space-3) var(--space-4)',
      marginBottom: 'var(--space-5)',
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-3)'
    }}>
      <div style={{ color: 'var(--accent-primary)', display: 'flex', alignItems: 'center' }}>
        <AlertCircle size={20} />
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 'var(--font-sm)', fontWeight: 700, color: 'var(--text-primary)' }}>
          {message}
        </div>
        <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '2px' }}>
          {subtext}
        </div>
      </div>
      <div className="badge badge-success" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
        <Terminal size={12} />
        <span>OPERATIONAL</span>
      </div>
    </div>
  );
};
