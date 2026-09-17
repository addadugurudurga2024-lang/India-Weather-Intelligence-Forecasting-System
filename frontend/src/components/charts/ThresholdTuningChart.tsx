import React from 'react';

interface ThresholdStep {
  threshold: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  fpr: number;
  fnr: number;
}

interface ThresholdTuningChartProps {
  title: string;
  sweep: ThresholdStep[];
  optimalThreshold: number;
  defaultThreshold?: number;
}

export const ThresholdTuningChart: React.FC<ThresholdTuningChartProps> = ({
  title,
  sweep,
  optimalThreshold,
  defaultThreshold = 0.5
}) => {
  const width = 380;
  const height = 280;
  const padding = { top: 20, right: 20, bottom: 40, left: 40 };

  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  const projectX = (t: number) => padding.left + t * chartW;
  const projectY = (v: number) => padding.top + (1 - v) * chartH;

  const precPath = sweep.reduce((acc, s, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${projectX(s.threshold)},${projectY(s.precision)}`, '');
  const recPath = sweep.reduce((acc, s, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${projectX(s.threshold)},${projectY(s.recall)}`, '');
  const f1Path = sweep.reduce((acc, s, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${projectX(s.threshold)},${projectY(s.f1)}`, '');

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ fontSize: 'var(--font-base)', fontWeight: 800, color: 'var(--text-primary)' }}>
            {title}
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Trade-off Across Decision Boundaries (τ)
          </div>
        </div>
        <div style={{ display: 'flex', gap: 'var(--space-1)' }}>
          <span className="badge badge-warning" style={{ fontSize: '10px' }}>
            F1-Opt: τ={optimalThreshold}
          </span>
        </div>
      </div>

      <div style={{ width: '100%', display: 'flex', justifyContent: 'center' }}>
        <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', maxWidth: '400px', height: 'auto' }}>
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1.0].map((v) => (
            <React.Fragment key={v}>
              <line
                x1={padding.left}
                y1={projectY(v)}
                x2={padding.left + chartW}
                y2={projectY(v)}
                stroke="var(--border-subtle)"
                strokeDasharray="3 3"
              />
              <text
                x={padding.left - 6}
                y={projectY(v) + 3}
                textAnchor="end"
                fontSize="9px"
                fill="var(--text-tertiary)"
              >
                {v.toFixed(2)}
              </text>
            </React.Fragment>
          ))}

          {/* Vertical Guides for Thresholds */}
          <line
            x1={projectX(optimalThreshold)}
            y1={padding.top}
            x2={projectX(optimalThreshold)}
            y2={padding.top + chartH}
            stroke="var(--accent-warning)"
            strokeWidth="1.5"
            strokeDasharray="3 3"
          />
          <line
            x1={projectX(defaultThreshold)}
            y1={padding.top}
            x2={projectX(defaultThreshold)}
            y2={padding.top + chartH}
            stroke="var(--text-tertiary)"
            strokeWidth="1.2"
            strokeDasharray="2 2"
          />

          {/* Curves */}
          <path d={precPath} fill="none" stroke="#38bdf8" strokeWidth="2" />
          <path d={recPath} fill="none" stroke="#f59e0b" strokeWidth="2" />
          <path d={f1Path} fill="none" stroke="#10b981" strokeWidth="2.5" />

          {/* X Axis ticks */}
          {[0.1, 0.3, 0.5, 0.7, 0.9].map((t) => (
            <text
              key={t}
              x={projectX(t)}
              y={padding.top + chartH + 16}
              textAnchor="middle"
              fontSize="9px"
              fill="var(--text-tertiary)"
            >
              {t.toFixed(1)}
            </text>
          ))}

          {/* X Axis Label */}
          <text
            x={padding.left + chartW / 2}
            y={height - 5}
            textAnchor="middle"
            fontSize="10px"
            fill="var(--text-secondary)"
            fontWeight="600"
          >
            Decision Threshold (τ)
          </text>
        </svg>
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--space-4)', fontSize: '11px' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#38bdf8' }} /> Precision
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f59e0b' }} /> Recall
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }} /> F1-Score
        </span>
      </div>
    </div>
  );
};
