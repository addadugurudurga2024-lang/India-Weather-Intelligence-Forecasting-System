import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  subtext: string;
  status?: 'normal' | 'info' | 'warning' | 'success';
  icon?: LucideIcon;
  sparklineData?: number[];
  badge?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  subtext,
  status = 'normal',
  icon: Icon,
  sparklineData,
  badge
}) => {
  const getAccentColor = () => {
    switch (status) {
      case 'info': return 'var(--accent-rain)';
      case 'warning': return 'var(--accent-warning)';
      case 'success': return 'var(--accent-success)';
      default: return 'var(--accent-primary)';
    }
  };

  const color = getAccentColor();

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: 'var(--font-xs)', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          {title}
        </span>
        {badge && <span className="badge badge-neutral">{badge}</span>}
        {Icon && (
          <div style={{
            width: '28px',
            height: '28px',
            borderRadius: 'var(--radius-sm)',
            background: `color-mix(in srgb, ${color} 15%, transparent)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: color
          }}>
            <Icon size={16} />
          </div>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: 'var(--space-2)' }}>
        <span style={{ fontSize: 'var(--font-3xl)', fontWeight: 800, letterSpacing: '-0.03em', color: 'var(--text-primary)' }}>
          {value}
        </span>
        {unit && (
          <span style={{ fontSize: 'var(--font-sm)', fontWeight: 600, color: color }}>
            {unit}
          </span>
        )}
      </div>

      {/* SVG Sparkline if available */}
      {sparklineData && sparklineData.length > 1 && (
        <div style={{ height: '24px', width: '100%' }}>
          <svg width="100%" height="100%" viewBox="0 0 100 24" preserveAspectRatio="none" style={{ overflow: 'visible' }}>
            {(() => {
              const min = Math.min(...sparklineData);
              const max = Math.max(...sparklineData);
              const range = max - min || 1;
              const points = sparklineData.map((val, idx) => {
                const x = (idx / (sparklineData.length - 1)) * 100;
                const y = 22 - ((val - min) / range) * 20;
                return `${x},${y}`;
              }).join(' ');

              return (
                <polyline
                  fill="none"
                  stroke={color}
                  strokeWidth="2.2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  points={points}
                />
              );
            })()}
          </svg>
        </div>
      )}

      <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)', marginTop: 'auto' }}>
        {subtext}
      </div>
    </div>
  );
};
