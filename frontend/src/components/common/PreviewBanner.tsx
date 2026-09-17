import React from 'react';
import { AlertCircle, Terminal } from 'lucide-react';

interface PreviewBannerProps {
  message?: string;
  subtext?: string;
}

export const PreviewBanner: React.FC<PreviewBannerProps> = ({
  message = 'Operational Preview • Phase 8.5 Architecture',
  subtext = 'FastAPI backend integration is scheduled for Phase 9. All operational intelligence reflects verified Phase 7 multi-horizon forecasting models and Phase 8 intelligence reasoning.'
}) => {
  return (
    <div style={{
      background: 'color-mix(in srgb, var(--accent-warning) 12%, var(--bg-surface))',
      border: '1px solid rgba(245, 158, 11, 0.3)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--space-3) var(--space-4)',
      marginBottom: 'var(--space-5)',
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-3)'
    }}>
      <div style={{ color: 'var(--accent-warning)', display: 'flex', alignItems: 'center' }}>
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
      <div className="badge badge-warning" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
        <Terminal size={12} />
        <span>DEV PREVIEW</span>
      </div>
    </div>
  );
};
