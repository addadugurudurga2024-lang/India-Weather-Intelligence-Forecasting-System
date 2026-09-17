import React from 'react';
import { Thermometer, Wind, Gauge, Droplets, Clock, MapPin, CheckCircle, AlertTriangle } from 'lucide-react';
import type { TimelineDayEntry, Operational25DayTimeline } from '../../types';

interface CurrentConditionsD0PanelProps {
  timelineData: Operational25DayTimeline;
  d0Entry?: TimelineDayEntry;
  timelineMode?: 'historical_holdout_replay' | 'operational_current';
}

export const CurrentConditionsD0Panel: React.FC<CurrentConditionsD0PanelProps> = ({ timelineData, d0Entry, timelineMode }) => {
  const current = d0Entry || timelineData.timeline.find((d) => d.relative_day === 0);
  const isReplay = timelineMode === 'historical_holdout_replay' || timelineData.forecast_origin === '2025-01-20';

  if (!current || current.status === 'UNAVAILABLE' || current.temperature_avg === null || !current.is_observed) {
    return (
      <div className="card" style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border-base)',
        padding: 'var(--space-6)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-3)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <AlertTriangle size={20} style={{ color: 'var(--accent-warning)' }} />
            <span style={{ fontSize: 'var(--font-lg)', fontWeight: 800, color: 'var(--text-primary)' }}>
              {isReplay ? 'REPLAY D0 • CONDITIONS (2025-01-20)' : 'TODAY • CURRENT CONDITIONS (D0)'}
            </span>
          </div>
          <span className="badge badge-warning">CURRENT DATA UNAVAILABLE</span>
        </div>
        <div style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-sm)', lineHeight: 1.6 }}>
          Telemetry for <strong>{timelineData.station_name}</strong> on {timelineData.forecast_origin} is currently unavailable from authoritative observation feeds (Source: UNAVAILABLE). In compliance with the <em>Zero Fabrication Rule</em>, no model estimate or synthetic value is substituted as current observation telemetry.
        </div>
      </div>
    );
  }

  const dateLabel = isReplay ? `Replay Anchor Date: 2025-01-20` : `Operational Date: ${current.date}`;

  return (
    <div className="card" style={{
      background: 'linear-gradient(135deg, color-mix(in srgb, var(--accent-primary) 12%, var(--bg-surface)) 0%, var(--bg-surface) 100%)',
      border: '1px solid var(--border-base)',
      padding: 'var(--space-6)',
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-5)'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-3)' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-1)' }}>
            <span className="badge badge-info" style={{ fontWeight: 800 }}>
              {isReplay ? 'REPLAY D0 • HISTORICAL CONDITIONS' : 'TODAY • CURRENT CONDITIONS (D0)'}
            </span>
            <span style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)' }}>
              {dateLabel}
            </span>
          </div>
          <div style={{ fontSize: 'var(--font-2xl)', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            {timelineData.station_name}
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginTop: '2px' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <MapPin size={12} /> {timelineData.district}, {timelineData.state} ({timelineData.elevation_m}m ASL)
            </span>
            <span>•</span>
            <span>Lat: {timelineData.latitude.toFixed(4)}°N, Lon: {timelineData.longitude.toFixed(4)}°E</span>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 'var(--space-1)' }}>
          <div className="badge badge-success" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <CheckCircle size={13} />
            <span>Telemetry Verified: OBSERVED</span>
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Clock size={11} /> Source: {current.provenance}
          </div>
        </div>
      </div>

      {/* Metric Tiles */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: 'var(--space-3)'
      }}>
        {/* Surface Temperature */}
        <div style={{
          background: 'var(--bg-surface-glass)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-4)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: 'var(--font-xs)', fontWeight: 700 }}>
            <span>AVERAGE TEMPERATURE</span>
            <Thermometer size={16} style={{ color: 'var(--accent-temp)' }} />
          </div>
          <div style={{ fontSize: 'var(--font-3xl)', fontWeight: 800, color: 'var(--accent-temp)', marginTop: 'var(--space-2)', fontFamily: 'var(--font-mono)' }}>
            {current.temperature_avg !== null ? `${current.temperature_avg}°C` : 'N/A'}
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)', marginTop: 'var(--space-1)' }}>
            Observed Extremes: Min {current.temperature_min ?? '--'}°C • Max {current.temperature_max ?? '--'}°C
          </div>
        </div>


        {/* Rainfall */}
        <div style={{
          background: 'var(--bg-surface-glass)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-4)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: 'var(--font-xs)', fontWeight: 700 }}>
            <span>DAILY PRECIPITATION</span>
            <Droplets size={16} style={{ color: 'var(--accent-rain)' }} />
          </div>
          <div style={{ fontSize: 'var(--font-3xl)', fontWeight: 800, color: 'var(--accent-rain)', marginTop: 'var(--space-2)', fontFamily: 'var(--font-mono)' }}>
            {current.rainfall_amount !== null ? `${current.rainfall_amount} mm` : 'N/A'}
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)', marginTop: 'var(--space-1)' }}>
            Status: {current.rainfall_amount !== null && current.rainfall_amount > 0 ? 'Precipitation Recorded' : 'Dry Day (0.0 mm)'}
          </div>
        </div>

        {/* Wind Speed */}
        <div style={{
          background: 'var(--bg-surface-glass)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-4)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: 'var(--font-xs)', fontWeight: 700 }}>
            <span>WIND SPEED</span>
            <Wind size={16} style={{ color: 'var(--accent-wind)' }} />
          </div>
          <div style={{ fontSize: 'var(--font-3xl)', fontWeight: 800, color: 'var(--accent-wind)', marginTop: 'var(--space-2)', fontFamily: 'var(--font-mono)' }}>
            {current.wind_speed !== null ? `${current.wind_speed} km/h` : 'N/A'}
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)', marginTop: 'var(--space-1)' }}>
            Horizontal anemometer speed
          </div>
        </div>

        {/* Atmospheric Pressure */}
        <div style={{
          background: 'var(--bg-surface-glass)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-4)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: 'var(--font-xs)', fontWeight: 700 }}>
            <span>BAROMETRIC PRESSURE</span>
            <Gauge size={16} style={{ color: 'var(--accent-pressure)' }} />
          </div>
          <div style={{ fontSize: 'var(--font-3xl)', fontWeight: 800, color: 'var(--accent-pressure)', marginTop: 'var(--space-2)', fontFamily: 'var(--font-mono)' }}>
            {current.air_pressure !== null ? `${current.air_pressure} hPa` : 'N/A'}
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)', marginTop: 'var(--space-1)' }}>
            Station barometer reading
          </div>
        </div>
      </div>
    </div>
  );
};
