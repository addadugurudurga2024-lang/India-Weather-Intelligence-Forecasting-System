import React from 'react';

interface ReliabilityBin {
  bin_range: string;
  mean_predicted_prob: number;
  empirical_rain_frequency: number;
  sample_count: number;
}

interface CalibrationDiagramChartProps {
  title: string;
  bins: ReliabilityBin[];
  ece: number;
  brierScore: number;
}

export const CalibrationDiagramChart: React.FC<CalibrationDiagramChartProps> = ({
  title,
  bins,
  ece,
  brierScore
}) => {
  const width = 360;
  const height = 280;
  const padding = { top: 20, right: 20, bottom: 40, left: 45 };

  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  const projectX = (prob: number) => padding.left + prob * chartW;
  const projectY = (freq: number) => padding.top + (1 - freq) * chartH;

  // Generate path string for model points
  const points = bins.map((b) => ({
    x: projectX(b.mean_predicted_prob),
    y: projectY(b.empirical_rain_frequency),
    ...b
  }));

  const pathD = points.reduce((acc, pt, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${pt.x},${pt.y}`, '');

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ fontSize: 'var(--font-base)', fontWeight: 800, color: 'var(--text-primary)' }}>
            {title}
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Holdout Probability vs Empirical Frequency
          </div>
        </div>
        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          <span className="badge badge-primary" style={{ fontSize: '10px' }}>
            ECE: {(ece * 100).toFixed(2)}%
          </span>
          <span className="badge badge-neutral" style={{ fontSize: '10px' }}>
            Brier: {brierScore.toFixed(4)}
          </span>
        </div>
      </div>

      <div style={{ width: '100%', display: 'flex', justifyContent: 'center' }}>
        <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', maxWidth: '380px', height: 'auto' }}>
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1.0].map((tick) => (
            <React.Fragment key={tick}>
              <line
                x1={padding.left}
                y1={projectY(tick)}
                x2={padding.left + chartW}
                y2={projectY(tick)}
                stroke="var(--border-subtle)"
                strokeDasharray="3 3"
              />
              <line
                x1={projectX(tick)}
                y1={padding.top}
                x2={projectX(tick)}
                y2={padding.top + chartH}
                stroke="var(--border-subtle)"
                strokeDasharray="3 3"
              />
              <text
                x={padding.left - 6}
                y={projectY(tick) + 3}
                textAnchor="end"
                fontSize="9px"
                fill="var(--text-tertiary)"
              >
                {tick.toFixed(2)}
              </text>
              <text
                x={projectX(tick)}
                y={padding.top + chartH + 16}
                textAnchor="middle"
                fontSize="9px"
                fill="var(--text-tertiary)"
              >
                {tick.toFixed(2)}
              </text>
            </React.Fragment>
          ))}

          {/* Perfect Calibration Diagonal (Reference Line) */}
          <line
            x1={projectX(0)}
            y1={projectY(0)}
            x2={projectX(1)}
            y2={projectY(1)}
            stroke="var(--text-tertiary)"
            strokeWidth="1.5"
            strokeDasharray="4 4"
          />

          {/* Model Curve */}
          <path
            d={pathD}
            fill="none"
            stroke="var(--accent-primary)"
            strokeWidth="2.5"
          />

          {/* Points */}
          {points.map((pt, i) => (
            <circle
              key={i}
              cx={pt.x}
              cy={pt.y}
              r="4"
              fill="var(--bg-app)"
              stroke="var(--accent-primary)"
              strokeWidth="2"
            />
          ))}

          {/* Axis Labels */}
          <text
            x={padding.left + chartW / 2}
            y={height - 5}
            textAnchor="middle"
            fontSize="10px"
            fill="var(--text-secondary)"
            fontWeight="600"
          >
            Mean Predicted Probability
          </text>
          <text
            x={12}
            y={padding.top + chartH / 2}
            textAnchor="middle"
            fontSize="10px"
            fill="var(--text-secondary)"
            fontWeight="600"
            transform={`rotate(-90 12 ${padding.top + chartH / 2})`}
          >
            Empirical Frequency
          </text>
        </svg>
      </div>

      <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', borderTop: '1px solid var(--border-subtle)', paddingTop: '6px' }}>
        Diagonal line indicates perfect calibration. Model shows robust alignment with low Expected Calibration Error (ECE = {ece.toFixed(4)}).
      </div>
    </div>
  );
};
