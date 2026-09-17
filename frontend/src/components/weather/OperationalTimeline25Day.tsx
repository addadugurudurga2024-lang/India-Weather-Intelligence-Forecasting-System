import React, { useState } from 'react';
import { Calendar, Droplets, ArrowLeft, ArrowRight, Eye } from 'lucide-react';
import type { Operational25DayTimeline, TimelineDayEntry } from '../../types';

interface OperationalTimeline25DayProps {
  timelineData: Operational25DayTimeline;
  onSelectDay?: (day: TimelineDayEntry) => void;
  timelineMode?: 'historical_holdout_replay' | 'operational_current';
}

export const OperationalTimeline25Day: React.FC<OperationalTimeline25DayProps> = ({ timelineData, onSelectDay, timelineMode }) => {
  const [selectedRelativeDay, setSelectedRelativeDay] = useState<number>(0);

  const isReplay = timelineMode === 'historical_holdout_replay' || timelineData.forecast_origin === '2025-01-20';
  const days = timelineData.timeline;
  const activeDay = days.find((d) => d.relative_day === selectedRelativeDay) || days[12]; // D0 default

  const handleCardClick = (day: TimelineDayEntry) => {
    setSelectedRelativeDay(day.relative_day);
    if (onSelectDay) onSelectDay(day);
  };

  const getStatusBadge = (status: string, _isObserved?: boolean) => {
    if (status === 'OBSERVED') {
      return (
        <span style={{
          background: 'rgba(16, 185, 129, 0.15)',
          color: '#10b981',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          padding: '2px 6px',
          borderRadius: '4px',
          fontSize: '9.5px',
          fontWeight: 800,
          letterSpacing: '0.04em'
        }}>
          OBSERVED
        </span>
      );
    }
    if (status === 'MODEL ESTIMATE') {
      return (
        <span style={{
          background: 'rgba(245, 158, 11, 0.15)',
          color: '#f59e0b',
          border: '1px solid rgba(245, 158, 11, 0.4)',
          padding: '2px 6px',
          borderRadius: '4px',
          fontSize: '9.5px',
          fontWeight: 800,
          letterSpacing: '0.04em'
        }}>
          MODEL ESTIMATE
        </span>
      );
    }
    if (status === 'CURRENT') {
      return (
        <span style={{
          background: 'rgba(14, 165, 233, 0.2)',
          color: '#0ea5e9',
          border: '1px solid rgba(14, 165, 233, 0.4)',
          padding: '2px 6px',
          borderRadius: '4px',
          fontSize: '9.5px',
          fontWeight: 800,
          letterSpacing: '0.04em'
        }}>
          {isReplay ? 'REPLAY D0' : 'TODAY'}
        </span>
      );
    }
    if (status === 'FORECAST') {
      return (
        <span style={{
          background: 'rgba(168, 85, 247, 0.15)',
          color: '#c084fc',
          border: '1px solid rgba(168, 85, 247, 0.3)',
          padding: '2px 6px',
          borderRadius: '4px',
          fontSize: '9.5px',
          fontWeight: 800,
          letterSpacing: '0.04em'
        }}>
          FORECAST
        </span>
      );
    }
    return (
      <span style={{
        background: 'rgba(239, 68, 68, 0.15)',
        color: '#ef4444',
        border: '1px solid rgba(239, 68, 68, 0.3)',
        padding: '2px 6px',
        borderRadius: '4px',
        fontSize: '9.5px',
        fontWeight: 800,
        letterSpacing: '0.04em'
      }}>
        UNAVAILABLE
      </span>
    );
  };

  return (
    <div className="card" style={{
      background: 'var(--bg-surface)',
      border: '1px solid var(--border-base)',
      padding: 'var(--space-5)',
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-4)'
    }}>
      {/* Top Controls & Navigation Header */}
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-3)' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <Calendar size={18} style={{ color: 'var(--accent-primary)' }} />
            <span style={{ fontSize: 'var(--font-lg)', fontWeight: 800, color: 'var(--text-primary)' }}>
              Operational 25-Day Chronological Weather Timeline
            </span>
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Zero-fabrication continuous sequence: 12 Measured Days • 1 Today (Current) • 12 Model Forecast Days
          </div>
        </div>

        {/* Quick jump anchors */}
        <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center' }}>
          <button
            onClick={() => setSelectedRelativeDay(-12)}
            className="btn btn-sm btn-secondary"
            style={{ fontSize: '11px', padding: '4px 10px' }}
          >
            ← Jump to Past (D-12)
          </button>
          <button
            onClick={() => setSelectedRelativeDay(0)}
            className="btn btn-sm btn-primary"
            style={{ fontSize: '11px', padding: '4px 12px', fontWeight: 800 }}
          >
            ● {isReplay ? 'Replay (D0)' : 'Today (D0)'}
          </button>
          <button
            onClick={() => setSelectedRelativeDay(12)}
            className="btn btn-sm btn-secondary"
            style={{ fontSize: '11px', padding: '4px 10px' }}
          >
            Jump to Day 12 (D+12) →
          </button>
        </div>
      </div>

      {/* Tri-Phase Section Headers */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '12fr 1.5fr 12fr',
        gap: '4px',
        textAlign: 'center',
        padding: '6px var(--space-2)',
        background: 'var(--bg-elevated)',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)',
        fontSize: '11px',
        fontWeight: 800,
        textTransform: 'uppercase',
        letterSpacing: '0.05em'
      }}>
        <div style={{ color: '#10b981', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
          <ArrowLeft size={13} /> {isReplay ? '12 Days Historical Context (D-12 to D-1)' : '12 Days Historical / Model Context (D-12 to D-1)'}
        </div>
        <div style={{ color: '#0ea5e9', borderLeft: '1px solid var(--border-base)', borderRight: '1px solid var(--border-base)', padding: '0 8px' }}>
          {isReplay ? 'Replay D0 (2025-01-20)' : 'Today (D0)'}
        </div>
        <div style={{ color: '#c084fc', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
          12 Days Model Forecasts (D+1 to D+12) <ArrowRight size={13} />
        </div>
      </div>

      {/* Horizontal Scrolling 25-Day Strip */}
      <div style={{
        display: 'flex',
        gap: 'var(--space-2)',
        overflowX: 'auto',
        paddingBottom: 'var(--space-3)',
        scrollSnapType: 'x mandatory'
      }}>
        {days.map((day) => {
          const isSelected = day.relative_day === selectedRelativeDay;
          const isCurrent = day.relative_day === 0;
          const isPast = day.relative_day < 0;

          // Border color styling by lifecycle phase
          let borderGlow = 'var(--border-subtle)';
          if (isSelected) borderGlow = 'var(--accent-primary)';
          else if (isCurrent) borderGlow = '#0ea5e9';
          else if (day.status === 'MODEL ESTIMATE') borderGlow = 'rgba(245, 158, 11, 0.4)';
          else if (isPast) borderGlow = 'rgba(16, 185, 129, 0.4)';
          else borderGlow = 'rgba(168, 85, 247, 0.4)';

          return (
            <div
              key={day.relative_day}
              onClick={() => handleCardClick(day)}
              style={{
                flex: '0 0 115px',
                scrollSnapAlign: 'start',
                cursor: 'pointer',
                background: isSelected
                  ? 'color-mix(in srgb, var(--accent-primary) 15%, var(--bg-surface))'
                  : isCurrent
                  ? 'color-mix(in srgb, #0ea5e9 10%, var(--bg-surface))'
                  : 'var(--bg-surface-glass)',
                border: `1.5px solid ${borderGlow}`,
                borderRadius: 'var(--radius-md)',
                padding: 'var(--space-3) var(--space-2)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '6px',
                transition: 'all 0.15s ease-in-out',
                transform: isSelected ? 'scale(1.02)' : 'none',
                boxShadow: isSelected ? '0 4px 12px rgba(0,0,0,0.12)' : 'none'
              }}
            >
              {/* Day Label & Badge */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '3px' }}>
                <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-primary)' }}>
                  {day.relative_day === 0 ? (isReplay ? 'REPLAY D0' : 'TODAY') : day.relative_day < 0 ? `D${day.relative_day}` : `D+${day.relative_day}`}
                </span>
                <span style={{ fontSize: '9.5px', color: 'var(--text-tertiary)' }}>
                  {day.date.slice(5)}
                </span>
                {getStatusBadge(day.status, day.is_observed)}
              </div>

              {/* Temperature */}
              <div style={{ marginTop: '2px', textAlign: 'center' }}>
                <div style={{ fontSize: 'var(--font-md)', fontWeight: 800, color: 'var(--accent-temp)', fontFamily: 'var(--font-mono)' }}>
                  {day.temperature_avg !== null ? `${day.temperature_avg}°C` : '--'}
                </div>
                {day.temperature_min !== null && day.temperature_max !== null && (
                  <div style={{ fontSize: '9px', color: 'var(--text-tertiary)' }}>
                    {day.temperature_min}° / {day.temperature_max}°
                  </div>
                )}
              </div>

              {/* Rainfall / Rain Risk */}
              <div style={{ textAlign: 'center' }}>
                {day.status === 'FORECAST' && day.rain_probability !== null ? (
                  <div style={{
                    fontSize: '9.5px',
                    fontWeight: 700,
                    color: day.rain_probability >= 0.30 ? 'var(--accent-rain)' : 'var(--text-tertiary)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '2px'
                  }}>
                    <Droplets size={10} />
                    <span>PoP: {Math.round(day.rain_probability * 100)}%</span>
                  </div>
                ) : (
                  <div style={{ fontSize: '9.5px', color: day.rainfall_amount && day.rainfall_amount > 0 ? 'var(--accent-rain)' : 'var(--text-tertiary)', display: 'flex', alignItems: 'center', gap: '2px' }}>
                    <Droplets size={10} />
                    <span>{day.rainfall_amount !== null ? `${day.rainfall_amount}mm` : '--'}</span>
                  </div>
                )}
              </div>

              {/* Uncertainty pill on forecasts (80% Prediction Interval) */}
              {day.uncertainty && (
                <div style={{
                  fontSize: '8px',
                  color: 'var(--text-tertiary)',
                  background: 'var(--bg-elevated)',
                  padding: '1px 4px',
                  borderRadius: '3px',
                  border: '1px solid var(--border-subtle)',
                  whiteSpace: 'nowrap'
                }} title="80% Prediction Interval (Empirical Residual Quantiles)">
                  [{day.uncertainty.temp_interval_80[0]}° - {day.uncertainty.temp_interval_80[1]}°] (80% PI)
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Selected Day Inspector Panel */}
      {activeDay && (
        <div style={{
          background: 'var(--bg-elevated)',
          border: '1px solid var(--border-base)',
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--space-4)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-3)'
        }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <Eye size={16} style={{ color: 'var(--accent-primary)' }} />
              <span style={{ fontSize: 'var(--font-sm)', fontWeight: 800, color: 'var(--text-primary)' }}>
                DAY INSPECTOR: {timelineData.station_name} • {activeDay.date} ({activeDay.relative_day === 0 ? (isReplay ? 'REPLAY D0 (2025-01-20)' : 'TODAY / D0 (Operational)') : activeDay.relative_day < 0 ? `Historical Context D${activeDay.relative_day}` : `Forecast Horizon D+${activeDay.relative_day}`})
              </span>
              {getStatusBadge(activeDay.status, activeDay.is_observed)}
            </div>

            <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
              <strong>Provenance:</strong> {activeDay.provenance}
            </div>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
            gap: 'var(--space-3)',
            marginTop: '2px'
          }}>
            <div style={{ padding: 'var(--space-2)', background: 'var(--bg-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', fontWeight: 700 }}>SURFACE TEMPERATURE (AVG)</div>
              <div style={{ fontSize: 'var(--font-lg)', fontWeight: 800, color: 'var(--accent-temp)', fontFamily: 'var(--font-mono)' }}>
                {activeDay.temperature_avg !== null ? `${activeDay.temperature_avg}°C` : 'Unavailable'}
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>
                Extremes: Min {activeDay.temperature_min ?? '--'}°C • Max {activeDay.temperature_max ?? '--'}°C
              </div>
            </div>

            <div style={{ padding: 'var(--space-2)', background: 'var(--bg-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', fontWeight: 700 }}>PRECIPITATION DEPTH</div>
              <div style={{ fontSize: 'var(--font-lg)', fontWeight: 800, color: 'var(--accent-rain)', fontFamily: 'var(--font-mono)' }}>
                {activeDay.rainfall_amount !== null ? `${activeDay.rainfall_amount} mm` : 'Unavailable'}
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>
                {activeDay.rain_probability !== null ? `Rain Occurrence Probability: ${Math.round(activeDay.rain_probability * 100)}%` : 'Direct Sensor Measurement'}
              </div>
            </div>

            <div style={{ padding: 'var(--space-2)', background: 'var(--bg-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', fontWeight: 700 }}>WIND SPEED</div>
              <div style={{ fontSize: 'var(--font-lg)', fontWeight: 800, color: 'var(--accent-wind)', fontFamily: 'var(--font-mono)' }}>
                {activeDay.wind_speed !== null ? `${activeDay.wind_speed} km/h` : 'Unavailable'}
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>
                Daily mean horizontal speed
              </div>
            </div>

            <div style={{ padding: 'var(--space-2)', background: 'var(--bg-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', fontWeight: 700 }}>BAROMETRIC PRESSURE</div>
              <div style={{ fontSize: 'var(--font-lg)', fontWeight: 800, color: 'var(--accent-pressure)', fontFamily: 'var(--font-mono)' }}>
                {activeDay.air_pressure !== null ? `${activeDay.air_pressure} hPa` : 'Unavailable'}
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>
                Station barometric pressure
              </div>
            </div>
          </div>

          {/* Uncertainty details if forecast */}
          {activeDay.uncertainty && (
            <div style={{
              fontSize: '11px',
              color: 'var(--text-secondary)',
              background: 'var(--bg-surface)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--space-3)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              flexWrap: 'wrap',
              gap: 'var(--space-4)',
              alignItems: 'center'
            }}>
              <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Validated Uncertainty Bounds:</span>
              <span>80% Prediction Interval: <strong>[{activeDay.uncertainty.temp_interval_80[0]}°C, {activeDay.uncertainty.temp_interval_80[1]}°C]</strong></span>
              <span>95% Interval: <strong>[{activeDay.uncertainty.temp_interval_95[0]}°C, {activeDay.uncertainty.temp_interval_95[1]}°C]</strong></span>
              <span style={{ color: 'var(--text-tertiary)' }}>• {activeDay.uncertainty.methodology}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
