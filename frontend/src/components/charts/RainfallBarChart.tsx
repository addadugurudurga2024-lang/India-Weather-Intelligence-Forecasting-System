import React, { useState } from 'react';
import type { WeatherObservation } from '../../types';

interface RainfallBarChartProps {
  data: WeatherObservation[];
  height?: number;
}

export const RainfallBarChart: React.FC<RainfallBarChartProps> = ({ data, height = 260 }) => {
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  if (!data || data.length === 0) {
    return <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-tertiary)' }}>No rainfall records available</div>;
  }

  const sorted = [...data].sort((a, b) => a.date_of_record.localeCompare(b.date_of_record));
  const maxRain = Math.max(5, Math.ceil(Math.max(...sorted.map((d) => d.rainfall ?? 0)) * 1.2));

  const padding = { top: 20, right: 25, bottom: 40, left: 45 };
  const width = 800;
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const barWidth = Math.max(3, Math.floor((chartWidth / sorted.length) * 0.75));
  const step = chartWidth / sorted.length;

  const hoveredItem = hoverIndex !== null ? sorted[hoverIndex] : null;

  return (
    <div style={{ width: '100%', position: 'relative' }}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        style={{ width: '100%', height: 'auto', overflow: 'visible' }}
        onMouseLeave={() => setHoverIndex(null)}
      >
        {/* Y Axis Grid */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
          const val = Math.round(ratio * maxRain * 10) / 10;
          const y = padding.top + (1 - ratio) * chartHeight;
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
                {val} mm
              </text>
            </g>
          );
        })}

        {/* Rainfall Bars */}
        {sorted.map((d, i) => {
          const x = padding.left + i * step + (step - barWidth) / 2;
          const rainVal = d.rainfall ?? 0;
          const barHeight = rainVal > 0 ? Math.max(4, (rainVal / maxRain) * chartHeight) : 2;
          const y = padding.top + chartHeight - barHeight;
          const isRainy = rainVal > 0;
          const isHovered = hoverIndex === i;

          return (
            <g key={d.date_of_record} onMouseEnter={() => setHoverIndex(i)}>
              {/* Hit area */}
              <rect
                x={padding.left + i * step}
                y={padding.top}
                width={step}
                height={chartHeight}
                fill="transparent"
                style={{ cursor: 'pointer' }}
              />

              {/* Bar */}
              <rect
                x={x}
                y={y}
                width={barWidth}
                height={barHeight}
                rx={1.5}
                fill={isRainy ? 'var(--accent-rain)' : 'var(--border-base)'}
                opacity={isHovered ? 1 : isRainy ? 0.85 : 0.4}
                style={{ transition: 'opacity 150ms' }}
              />
            </g>
          );
        })}

        {/* X Axis Labels */}
        {sorted.filter((_, idx) => idx % Math.ceil(sorted.length / 6) === 0).map((d) => {
          const idx = sorted.indexOf(d);
          const x = padding.left + idx * step + step / 2;
          return (
            <text
              key={d.date_of_record}
              x={x}
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
            left: `${((padding.left + hoverIndex * step + step / 2) / width) * 100}%`,
            top: '8px',
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
          <div style={{ fontSize: 'var(--font-xs)', marginTop: '2px', color: (hoveredItem.rainfall ?? 0) > 0 ? 'var(--accent-rain)' : 'var(--text-secondary)' }}>
            {hoveredItem.rainfall === null 
              ? 'Observation Missing' 
              : hoveredItem.rainfall > 0 
                ? `Rain: ${hoveredItem.rainfall} mm (Active Rain)` 
                : 'Dry: 0.0 mm (No Rain)'}
          </div>
        </div>
      )}
    </div>
  );
};
