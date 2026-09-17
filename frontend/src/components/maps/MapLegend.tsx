import React from 'react';
import type { MapLayerId } from '../../types/geospatial';

interface MapLegendProps {
  activeLayer: MapLayerId;
  activeMetric?: string;
}

export const MapLegend: React.FC<MapLegendProps> = ({ activeLayer, activeMetric }) => {
  return (
    <div style={{
      background: 'var(--bg-surface-glass)',
      backdropFilter: 'blur(10px)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--space-3) var(--space-4)',
      boxShadow: 'var(--shadow-md)',
      fontSize: 'var(--font-2xs)',
      color: 'var(--text-secondary)',
      display: 'flex',
      flexDirection: 'column',
      gap: '6px',
      maxWidth: '280px'
    }}>
      {/* Legend Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '4px' }}>
        <span style={{ fontWeight: 800, color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          {activeLayer === 'temperature' && 'Temperature Scale (°C)'}
          {activeLayer === 'rainfall' && 'IMD Rainfall Classification'}
          {activeLayer === 'elevation' && 'Hypsometric Topography (m)'}
          {activeLayer === 'stations' && 'Station Status & Network'}
          {activeLayer === 'state_density' && 'State Station Density'}
          {activeLayer === 'forecast_overlay' && 'XGBoost Prediction Scale'}
        </span>
        <span style={{
          fontSize: '9px',
          fontWeight: 700,
          padding: '1px 5px',
          borderRadius: '3px',
          background: activeLayer === 'forecast_overlay' ? 'var(--accent-warning)' : 'var(--bg-surface-elevated)',
          color: activeLayer === 'forecast_overlay' ? '#000' : 'var(--text-tertiary)'
        }}>
          {activeLayer === 'forecast_overlay' ? 'FORECAST' : 'OBSERVED'}
        </span>
      </div>

      {/* Temperature Legend */}
      {activeLayer === 'temperature' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#818cf8' }} />
            <span>&lt; 5°C (Cold / Himalayan)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#38bdf8' }} />
            <span>5°C – 12°C (Cool)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#2dd4bf' }} />
            <span>12°C – 18°C (Mild)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#34d399' }} />
            <span>18°C – 24°C (Pleasant)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#facc15' }} />
            <span>24°C – 29°C (Warm)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#fb923c' }} />
            <span>29°C – 34°C (Hot)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#f43f5e' }} />
            <span>≥ 34°C (Extreme Heat)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', borderTop: '1px dashed var(--border-subtle)', paddingTop: '3px', marginTop: '2px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#64748b' }} />
            <span style={{ color: 'var(--text-tertiary)', fontStyle: 'italic' }}>Missing / Not Reported</span>
          </div>
        </div>
      )}

      {/* Rainfall Legend */}
      {activeLayer === 'rainfall' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#94a3b8' }} />
            <span>Dry Day (0.0 mm)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#7dd3fc' }} />
            <span>Very Light (&lt; 2.5 mm)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#38bdf8' }} />
            <span>Light (2.5 – 7.5 mm)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#0284c7' }} />
            <span>Moderate (7.6 – 35.5 mm)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#f59e0b' }} />
            <span>Rather Heavy (35.6 – 64.4 mm)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ef4444' }} />
            <span>Heavy (64.5 – 124.4 mm)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#dc2626' }} />
            <span>Very Heavy (≥ 124.5 mm)</span>
          </div>
          {/* Explicit missing distinction */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', borderTop: '1px dashed var(--border-subtle)', paddingTop: '3px', marginTop: '2px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#64748b' }} />
            <span style={{ color: 'var(--accent-warning)', fontWeight: 700 }}>Missing Observation (≠ 0mm)</span>
          </div>
        </div>
      )}

      {/* Elevation Legend */}
      {activeLayer === 'elevation' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#c084fc' }} />
            <span>≥ 1500m (High Himalayan)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#a855f7' }} />
            <span>1000m – 1499m (Sub-Himalayan / Ghats)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#38bdf8' }} />
            <span>600m – 999m (Deccan Plateau)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#34d399' }} />
            <span>300m – 599m (High Plains)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#2dd4bf' }} />
            <span>&lt; 300m (Coastal / Low Plains)</span>
          </div>
        </div>
      )}

      {/* Stations Legend */}
      {activeLayer === 'stations' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--accent-primary)' }} />
            <span>Active Canonical Station (413 total)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', border: '2px solid var(--accent-warning)', background: 'transparent' }} />
            <span>Selected Station Focus</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#38bdf8' }} />
            <span>Hovered Telemetry Point</span>
          </div>
        </div>
      )}

      {/* State Density Legend */}
      {activeLayer === 'state_density' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '2px', background: '#38bdf8' }} />
            <span>High Density (&gt; 25 Stations)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '2px', background: '#34d399' }} />
            <span>Medium Density (10 – 25 Stations)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '2px', background: '#facc15' }} />
            <span>Moderate Density (5 – 9 Stations)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '2px', background: '#94a3b8' }} />
            <span>Sparse Density (&lt; 5 Stations)</span>
          </div>
          <div style={{ fontSize: '9px', color: 'var(--text-tertiary)', fontStyle: 'italic', marginTop: '2px' }}>
            * Note: State averages are derived aggregates, not single station measurements.
          </div>
        </div>
      )}

      {/* Forecast Overlay Legend */}
      {activeLayer === 'forecast_overlay' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {activeMetric === 'rain_probability' ? (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ef4444' }} />
                <span>Severe Rain Risk (&ge; 70% Prob)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#f59e0b' }} />
                <span>High Potential (50% – 69%)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#38bdf8' }} />
                <span>Elevated Potential (35% – 49%)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#10b981' }} />
                <span>Low Rain Probability (&lt; 35%)</span>
              </div>
            </>
          ) : activeMetric === 'predicted_rainfall' ? (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ef4444' }} />
                <span>Heavy Rain (&ge; 35 mm)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#f59e0b' }} />
                <span>Moderate Rain (7.5 – 34.9 mm)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#38bdf8' }} />
                <span>Light Rain (2.5 – 7.4 mm)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#94a3b8' }} />
                <span>Dry / Near Zero (&lt; 2.5 mm)</span>
              </div>
            </>
          ) : (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#f43f5e' }} />
                <span>Hot (&ge; 30°C)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#34d399' }} />
                <span>Moderate (15°C – 29°C)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#38bdf8' }} />
                <span>Cool (&lt; 15°C)</span>
              </div>
            </>
          )}
          <div style={{ fontSize: '9px', color: 'var(--text-tertiary)', fontStyle: 'italic', marginTop: '2px' }}>
            Model: XGBoost Holdout Benchmark Candidate
          </div>
        </div>
      )}
    </div>
  );
};
