import React from 'react';
import {
  MapPin,
  Thermometer,
  CloudRain,
  Mountain,
  Grid,
  Zap
} from 'lucide-react';
import type { MapLayerId } from '../../types/geospatial';

interface LayerControlProps {
  activeLayer: MapLayerId;
  onLayerChange: (layer: MapLayerId) => void;
  activeMetric?: string;
  onMetricChange?: (metric: string) => void;
}

interface LayerOption {
  id: MapLayerId;
  label: string;
  icon: React.ComponentType<{ size?: number; className?: string; style?: React.CSSProperties }>;
  description: string;
  badge?: string;
  metrics?: { id: string; label: string }[];
}

const LAYERS: LayerOption[] = [
  {
    id: 'stations',
    label: 'Stations',
    icon: MapPin,
    description: '413 Physical Telemetry Stations',
    metrics: [
      { id: 'default', label: 'Standard Points' },
      { id: 'elevation_split', label: 'Elevation Grouping' }
    ]
  },
  {
    id: 'temperature',
    label: 'Temperature',
    icon: Thermometer,
    description: 'Observed Daily Temperature (°C)',
    metrics: [
      { id: 'avg_temp', label: 'Average Temp' },
      { id: 'min_temp', label: 'Minimum Temp' },
      { id: 'max_temp', label: 'Maximum Temp' }
    ]
  },
  {
    id: 'rainfall',
    label: 'Rainfall',
    icon: CloudRain,
    description: 'IMD Classified Rainfall (mm)',
    metrics: [
      { id: 'amount_mm', label: 'Rain Amount (mm)' },
      { id: 'intensity_class', label: 'IMD Intensity' },
      { id: 'is_rainy', label: 'Rainy vs Dry' }
    ]
  },
  {
    id: 'elevation',
    label: 'Elevation',
    icon: Mountain,
    description: 'Hypsometric Topography (m)',
    metrics: [
      { id: 'elevation_m', label: 'Topographic Altitude' }
    ]
  },
  {
    id: 'state_density',
    label: 'State Density',
    icon: Grid,
    description: 'Regional Station Density & Aggregates',
    metrics: [
      { id: 'density', label: 'Station Density' },
      { id: 'state_temp', label: 'State Mean Temp' }
    ]
  },
  {
    id: 'forecast_overlay',
    label: 'XGBoost Forecast',
    icon: Zap,
    description: 'Phase 3 Production Candidate (Holdout)',
    badge: 'XGBoost',
    metrics: [
      { id: 'predicted_temp', label: 'Next-Day Temp' },
      { id: 'predicted_rainfall', label: 'Next-Day Rain (mm)' },
      { id: 'rain_probability', label: 'Rain Probability' }
    ]
  }
];

export const LayerControl: React.FC<LayerControlProps> = ({
  activeLayer,
  onLayerChange,
  activeMetric,
  onMetricChange
}) => {
  const currentLayerConfig = LAYERS.find((l) => l.id === activeLayer);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-2)',
      background: 'var(--bg-surface-glass)',
      backdropFilter: 'blur(12px)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 'var(--radius-lg)',
      padding: 'var(--space-3)',
      boxShadow: 'var(--shadow-md)',
      maxWidth: '100%'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '2px'
      }}>
        <span style={{
          fontSize: 'var(--font-xs)',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          color: 'var(--text-tertiary)'
        }}>
          Geospatial Map Layers
        </span>
        <span className="badge badge-primary" style={{ fontSize: '10px' }}>
          Phase 5
        </span>
      </div>

      {/* Layer selector pills */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: 'var(--space-1)',
        alignItems: 'center'
      }}>
        {LAYERS.map((layer) => {
          const Icon = layer.icon;
          const isActive = activeLayer === layer.id;

          return (
            <button
              key={layer.id}
              onClick={() => {
                onLayerChange(layer.id);
                if (layer.metrics && layer.metrics.length > 0 && onMetricChange) {
                  onMetricChange(layer.metrics[0].id);
                }
              }}
              className={`btn ${isActive ? 'btn-primary' : 'btn-ghost'}`}
              style={{
                fontSize: 'var(--font-xs)',
                padding: '6px 10px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                borderRadius: 'var(--radius-md)',
                cursor: 'pointer',
                transition: 'all var(--transition-fast)'
              }}
              title={layer.description}
            >
              <Icon size={14} />
              <span>{layer.label}</span>
              {layer.badge && (
                <span style={{
                  fontSize: '9px',
                  padding: '1px 4px',
                  borderRadius: '3px',
                  background: isActive ? 'rgba(255,255,255,0.25)' : 'var(--accent-primary)',
                  color: '#fff',
                  fontWeight: 800
                }}>
                  {layer.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Sub-metric options if available for current layer */}
      {currentLayerConfig?.metrics && currentLayerConfig.metrics.length > 1 && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-2)',
          marginTop: 'var(--space-1)',
          paddingTop: 'var(--space-2)',
          borderTop: '1px solid var(--border-subtle)',
          fontSize: 'var(--font-xs)',
          color: 'var(--text-secondary)'
        }}>
          <span style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-tertiary)' }}>Metric:</span>
          <div style={{ display: 'flex', gap: 'var(--space-1)', flexWrap: 'wrap' }}>
            {currentLayerConfig.metrics.map((m) => {
              const isSelected = activeMetric === m.id;
              return (
                <button
                  key={m.id}
                  onClick={() => onMetricChange && onMetricChange(m.id)}
                  style={{
                    border: '1px solid',
                    borderColor: isSelected ? 'var(--accent-primary)' : 'var(--border-subtle)',
                    background: isSelected ? 'var(--bg-surface-elevated)' : 'transparent',
                    color: isSelected ? 'var(--accent-primary)' : 'var(--text-secondary)',
                    fontWeight: isSelected ? 700 : 500,
                    padding: '3px 8px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '11px',
                    cursor: 'pointer'
                  }}
                >
                  {m.label}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
