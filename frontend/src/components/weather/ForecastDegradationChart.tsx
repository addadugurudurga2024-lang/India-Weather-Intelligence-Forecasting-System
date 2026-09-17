import React, { useState } from 'react';
import { TrendingUp, AlertCircle } from 'lucide-react';
import type { MultiHorizonSummary } from '../../types';

interface ForecastDegradationChartProps {
  summary: MultiHorizonSummary;
}

export const ForecastDegradationChart: React.FC<ForecastDegradationChartProps> = ({ summary }) => {
  const [activeMetric, setActiveMetric] = useState<'temp' | 'rainfall' | 'roc_auc'>('temp');

  const horizons = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
  const deg = summary.skill_degradation;

  // Chart configuration
  const width = 640;
  const height = 240;
  const padLeft = 50;
  const padRight = 30;
  const padTop = 30;
  const padBottom = 40;

  const chartW = width - padLeft - padRight;
  const chartH = height - padTop - padBottom;

  let values: number[] = [];
  let yMin = 0;
  let yMax = 1;
  let unit = '';
  let title = '';

  if (activeMetric === 'temp') {
    values = deg.avg_temp_mae;
    yMin = 0.5;
    yMax = 1.6;
    unit = '°C';
    title = 'Mean Absolute Error (MAE) Across Horizons';
  } else if (activeMetric === 'rainfall') {
    values = deg.rainfall_mae;
    yMin = 0.35;
    yMax = 0.60;
    unit = 'mm';
    title = 'Rainfall MAE (mm) Across Horizons';
  } else {
    values = deg.rain_binary_roc_auc;
    yMin = 0.60;
    yMax = 0.90;
    unit = 'AUC';
    title = 'Rain Occurrence ROC-AUC Across Horizons';
  }

  const getX = (idx: number) => padLeft + (idx / (horizons.length - 1)) * chartW;
  const getY = (val: number) => padTop + chartH - ((val - yMin) / (yMax - yMin)) * chartH;

  const points = values.map((v, i) => `${getX(i)},${getY(v)}`).join(' ');

  return (
    <div className="card" style={{
      background: 'var(--bg-surface)',
      border: '1px solid var(--border-base)',
      padding: 'var(--space-5)',
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-4)'
    }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-3)' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <TrendingUp size={18} style={{ color: 'var(--accent-primary)' }} />
            <span style={{ fontSize: 'var(--font-md)', fontWeight: 800, color: 'var(--text-primary)' }}>
              12-Day Forecast Skill Degradation (T+1 to T+12)
            </span>
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '2px' }}>
            {title} &bull; Empirical out-of-time validation error progression on 2025 holdout partition
          </div>
        </div>

        {/* Metric Selector Buttons */}
        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          <button
            onClick={() => setActiveMetric('temp')}
            className={`btn btn-sm ${activeMetric === 'temp' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '11px', padding: '4px 10px' }}
          >
            Temperature MAE
          </button>
          <button
            onClick={() => setActiveMetric('rainfall')}
            className={`btn btn-sm ${activeMetric === 'rainfall' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '11px', padding: '4px 10px' }}
          >
            Rainfall Amount
          </button>
          <button
            onClick={() => setActiveMetric('roc_auc')}
            className={`btn btn-sm ${activeMetric === 'roc_auc' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '11px', padding: '4px 10px' }}
          >
            Rain ROC-AUC
          </button>
        </div>
      </div>

      {/* SVG Chart */}
      <div style={{ width: '100%', overflowX: 'auto' }}>
        <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', maxHeight: '240px' }}>
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1.0].map((ratio) => {
            const y = padTop + chartH * (1 - ratio);
            const labelVal = (yMin + ratio * (yMax - yMin)).toFixed(2);
            return (
              <g key={ratio}>
                <line x1={padLeft} y1={y} x2={width - padRight} y2={y} stroke="var(--border-subtle)" strokeDasharray="3 3" />
                <text x={padLeft - 8} y={y + 4} textAnchor="end" fontSize="10" fill="var(--text-tertiary)">
                  {labelVal}{unit}
                </text>
              </g>
            );
          })}

          {/* Critical Operational Horizon Markers */}
          <line x1={getX(6)} y1={padTop} x2={getX(6)} y2={padTop + chartH} stroke="var(--accent-warning)" strokeDasharray="4 4" opacity="0.6" />
          <text x={getX(6)} y={padTop - 8} textAnchor="middle" fontSize="10" fill="var(--accent-warning)" fontWeight="700">
            Day 7 Limit
          </text>

          {/* Area fill under curve */}
          <polygon
            points={`${getX(0)},${padTop + chartH} ${points} ${getX(horizons.length - 1)},${padTop + chartH}`}
            fill="var(--accent-primary)"
            opacity="0.12"
          />

          {/* Line */}
          <polyline
            points={points}
            fill="none"
            stroke="var(--accent-primary)"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Data Points */}
          {values.map((val, idx) => {
            const x = getX(idx);
            const y = getY(val);
            return (
              <g key={idx}>
                <circle cx={x} cy={y} r="4.5" fill="var(--accent-primary)" stroke="var(--bg-surface)" strokeWidth="2" />
                <text x={x} y={y - 8} textAnchor="middle" fontSize="9.5" fontWeight="700" fill="var(--text-primary)">
                  {val.toFixed(2)}
                </text>
                <text x={x} y={padTop + chartH + 18} textAnchor="middle" fontSize="10" fill="var(--text-secondary)" fontWeight="600">
                  T+{horizons[idx]}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Scientific takeaway alert */}
      <div style={{
        background: 'color-mix(in srgb, var(--accent-info) 8%, var(--bg-surface))',
        border: '1px solid color-mix(in srgb, var(--accent-info) 20%, transparent)',
        borderRadius: 'var(--radius-md)',
        padding: 'var(--space-3)',
        fontSize: 'var(--font-xs)',
        color: 'var(--text-secondary)',
        display: 'flex',
        alignItems: 'flex-start',
        gap: 'var(--space-2)'
      }}>
        <AlertCircle size={15} style={{ color: 'var(--accent-info)', flexShrink: 0, marginTop: '2px' }} />
        <div>
          <strong>Scientific Takeaway:</strong> Temperature forecasting remains strongly skilled through Day 7 (MAE 1.16&deg;C vs persistence 1.52&deg;C), after which error increases towards climatological background noise at Day 12 (1.30&deg;C). Precipitation discrimination is high at short horizons (ROC-AUC 0.83 at T+1) but gradually decays towards 0.78 by Day 12.
        </div>
      </div>
    </div>
  );
};
