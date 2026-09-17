import React, { useState } from 'react';
import type { WeatherObservation } from '../../types';

interface TemperatureTrendChartProps {
  data: WeatherObservation[];
  height?: number;
}

export const TemperatureTrendChart: React.FC<TemperatureTrendChartProps> = ({ data, height = 300 }) => {
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  if (!data || data.length === 0) {
    return <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-tertiary)' }}>No temperature data available</div>;
  }

  // Sort chronologically
  const sorted = [...data].sort((a, b) => a.date_of_record.localeCompare(b.date_of_record));
  const valid = sorted.filter((d) => d.avg_temp !== null);

  if (valid.length === 0) return <div>No valid records</div>;

  const minVal = Math.floor(Math.min(...valid.map((d) => d.min_temp ?? d.avg_temp ?? 0)) - 2);
  const maxVal = Math.ceil(Math.max(...valid.map((d) => d.max_temp ?? d.avg_temp ?? 35)) + 2);
  const range = maxVal - minVal || 1;

  const padding = { top: 20, right: 30, bottom: 40, left: 45 };
  const width = 800; // viewBox width

  const getX = (i: number) => padding.left + (i / (valid.length - 1 || 1)) * (width - padding.left - padding.right);
  const getY = (temp: number) => padding.top + (1 - (temp - minVal) / range) * (height - padding.top - padding.bottom);

  // Area polygon for min to max envelope
  const envelopePoints: string[] = [];
  // Top curve (max_temp)
  valid.forEach((d, i) => {
    const y = getY(d.max_temp ?? d.avg_temp ?? 0);
    envelopePoints.push(`${getX(i)},${y}`);
  });
  // Bottom curve (min_temp in reverse)
  for (let i = valid.length - 1; i >= 0; i--) {
    const d = valid[i];
    const y = getY(d.min_temp ?? d.avg_temp ?? 0);
    envelopePoints.push(`${getX(i)},${y}`);
  }

  // Line points for avg_temp
  const avgPoints = valid.map((d, i) => `${getX(i)},${getY(d.avg_temp as number)}`).join(' ');

  const hoveredItem = hoverIndex !== null ? valid[hoverIndex] : null;

  return (
    <div style={{ width: '100%', position: 'relative' }}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        style={{ width: '100%', height: 'auto', overflow: 'visible' }}
        onMouseLeave={() => setHoverIndex(null)}
      >
        <defs>
          <linearGradient id="tempEnvelopeGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--accent-temp)" stopOpacity="0.25" />
            <stop offset="100%" stopColor="var(--accent-primary)" stopOpacity="0.05" />
          </linearGradient>
        </defs>

        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
          const temp = Math.round(minVal + ratio * range);
          const y = getY(temp);
          return (
            <g key={ratio}>
              <line
                x1={padding.left}
                y1={y}
                x2={width - padding.right}
                y2={y}
                stroke="var(--chart-grid)"
                strokeDasharray="4 4"
              />
              <text
                x={padding.left - 8}
                y={y + 4}
                textAnchor="end"
                fontSize="11"
                fill="var(--text-tertiary)"
                fontFamily="var(--font-mono)"
              >
                {temp}°C
              </text>
            </g>
          );
        })}

        {/* Min-Max Temperature Envelope */}
        <polygon points={envelopePoints.join(' ')} fill="url(#tempEnvelopeGrad)" />

        {/* Average Temperature Polyline */}
        <polyline
          fill="none"
          stroke="var(--accent-temp)"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={avgPoints}
        />

        {/* Interactive Hover Zones */}
        {valid.map((d, i) => {
          const cx = getX(i);
          const cy = getY(d.avg_temp as number);
          const isHovered = hoverIndex === i;

          return (
            <g key={d.date_of_record} onMouseEnter={() => setHoverIndex(i)}>
              {/* Invisible touch/mouse target */}
              <rect
                x={cx - 10}
                y={padding.top}
                width={20}
                height={height - padding.top - padding.bottom}
                fill="transparent"
                style={{ cursor: 'crosshair' }}
              />

              {isHovered && (
                <>
                  <line
                    x1={cx}
                    y1={padding.top}
                    x2={cx}
                    y2={height - padding.bottom}
                    stroke="var(--accent-primary)"
                    strokeWidth="1.5"
                    strokeDasharray="2 2"
                  />
                  <circle cx={cx} cy={cy} r="5" fill="var(--accent-temp)" stroke="var(--bg-surface)" strokeWidth="2" />
                </>
              )}
            </g>
          );
        })}

        {/* Date labels on X-axis (sample 6 dates) */}
        {valid.filter((_, idx) => idx % Math.ceil(valid.length / 6) === 0).map((d) => {
          const idx = valid.indexOf(d);
          return (
            <text
              key={d.date_of_record}
              x={getX(idx)}
              y={height - padding.bottom + 18}
              textAnchor="middle"
              fontSize="11"
              fill="var(--text-tertiary)"
            >
              {d.date_of_record.slice(5)}
            </text>
          );
        })}
      </svg>

      {/* Floating Tooltip */}
      {hoveredItem && hoverIndex !== null && (
        <div
          style={{
            position: 'absolute',
            left: `${(getX(hoverIndex) / width) * 100}%`,
            top: '10px',
            transform: 'translateX(-50%)',
            background: 'var(--chart-tooltip-bg)',
            border: '1px solid var(--border-base)',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--space-2) var(--space-3)',
            boxShadow: 'var(--shadow-md)',
            pointerEvents: 'none',
            zIndex: 'var(--z-tooltip)',
            whiteSpace: 'nowrap'
          }}
        >
          <div style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-primary)' }}>
            {hoveredItem.date_of_record}
          </div>
          <div style={{ display: 'flex', gap: 'var(--space-3)', marginTop: '4px', fontSize: 'var(--font-xs)' }}>
            <span style={{ color: 'var(--accent-temp)', fontWeight: 600 }}>Avg: {hoveredItem.avg_temp}°C</span>
            <span style={{ color: 'var(--text-secondary)' }}>Min: {hoveredItem.min_temp}°C</span>
            <span style={{ color: 'var(--text-secondary)' }}>Max: {hoveredItem.max_temp}°C</span>
          </div>
        </div>
      )}
    </div>
  );
};
