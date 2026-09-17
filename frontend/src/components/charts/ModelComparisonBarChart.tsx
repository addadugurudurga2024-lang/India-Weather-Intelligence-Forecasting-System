import React from 'react';

interface ModelComparisonBarChartProps {
  title: string;
  metricLabel: string;
  unit?: string;
  lowerIsBetter?: boolean;
  models: {
    name: string;
    value: number;
    color: string;
    isPrimary?: boolean;
  }[];
}

export const ModelComparisonBarChart: React.FC<ModelComparisonBarChartProps> = ({
  title,
  metricLabel,
  unit = '',
  lowerIsBetter = true,
  models
}) => {
  const values = models.map((m) => m.value);
  const maxVal = Math.max(...values) * 1.15 || 1;

  // Best model determination
  const bestVal = lowerIsBetter ? Math.min(...values) : Math.max(...values);

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontSize: 'var(--font-sm)', fontWeight: 700, color: 'var(--text-primary)' }}>
            {title}
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)' }}>
            {metricLabel} {unit ? `(${unit})` : ''} • {lowerIsBetter ? 'Lower is better' : 'Higher is better'}
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
        {models.map((model) => {
          const isBest = model.value === bestVal;
          const percentage = Math.max(8, (model.value / maxVal) * 100);

          return (
            <div key={model.name} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 'var(--font-xs)' }}>
                <span style={{ fontWeight: model.isPrimary ? 700 : 500, color: model.isPrimary ? 'var(--accent-primary)' : 'var(--text-secondary)' }}>
                  {model.name} {model.isPrimary && '(Candidate)'}
                </span>
                <span style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', color: isBest ? 'var(--accent-success)' : 'var(--text-primary)' }}>
                  {model.value.toFixed(4)} {unit}
                </span>
              </div>

              <div style={{
                height: '18px',
                background: 'var(--bg-surface-elevated)',
                borderRadius: 'var(--radius-sm)',
                overflow: 'hidden',
                position: 'relative'
              }}>
                <div
                  style={{
                    height: '100%',
                    width: `${percentage}%`,
                    background: model.color,
                    borderRadius: 'var(--radius-sm)',
                    transition: 'width var(--transition-smooth)'
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
