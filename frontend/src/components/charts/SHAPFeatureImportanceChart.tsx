import React from 'react';

interface SHAPFeatureItem {
  feature: string;
  mean_abs_shap: number;
  direction: string;
  correlation: number;
}

interface SHAPFeatureImportanceChartProps {
  title: string;
  subtitle?: string;
  features: SHAPFeatureItem[];
  unitLabel: string;
  primaryColor?: string;
}

export const SHAPFeatureImportanceChart: React.FC<SHAPFeatureImportanceChartProps> = ({
  title,
  subtitle,
  features,
  unitLabel,
  primaryColor = 'var(--accent-primary)'
}) => {
  const top10 = features.slice(0, 10);
  const maxVal = Math.max(...top10.map((f) => f.mean_abs_shap), 0.001);

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      <div>
        <div style={{ fontSize: 'var(--font-base)', fontWeight: 800, color: 'var(--text-primary)' }}>
          {title}
        </div>
        {subtitle && (
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '2px' }}>
            {subtitle}
          </div>
        )}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: 'var(--space-2)' }}>
        {top10.map((item, idx) => {
          const widthPct = Math.min(100, Math.max(4, (item.mean_abs_shap / maxVal) * 100));
          const isTop = idx === 0;

          return (
            <div key={item.feature} style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-xs)' }}>
                <span style={{ fontWeight: isTop ? 700 : 500, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ color: 'var(--text-tertiary)', fontSize: '10px' }}>#{idx + 1}</span>
                  <code>{item.feature}</code>
                </span>
                <span style={{ fontWeight: 700, color: primaryColor }}>
                  {item.mean_abs_shap.toFixed(4)} {unitLabel}
                </span>
              </div>

              {/* Progress Bar */}
              <div style={{
                height: '8px',
                width: '100%',
                background: 'var(--bg-surface-elevated)',
                borderRadius: 'var(--radius-sm)',
                overflow: 'hidden',
                position: 'relative'
              }}>
                <div style={{
                  height: '100%',
                  width: `${widthPct}%`,
                  background: isTop ? primaryColor : 'color-mix(in srgb, var(--accent-primary) 70%, var(--bg-surface-elevated))',
                  borderRadius: 'var(--radius-sm)',
                  transition: 'width 300ms ease-out'
                }} />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '9px', color: 'var(--text-tertiary)' }}>
                <span>Association: {item.direction.replace('_', ' ')}</span>
                <span>Corr: {item.correlation > 0 ? `+${item.correlation}` : item.correlation}</span>
              </div>
            </div>
          );
        })}
      </div>

      <div style={{
        fontSize: '10px',
        color: 'var(--text-tertiary)',
        borderTop: '1px solid var(--border-subtle)',
        paddingTop: 'var(--space-2)',
        marginTop: 'var(--space-1)',
        fontStyle: 'italic'
      }}>
        * Scientific Note: Mean |SHAP| attributions reflect empirical model sensitivity, not physical atmospheric causation.
      </div>
    </div>
  );
};
