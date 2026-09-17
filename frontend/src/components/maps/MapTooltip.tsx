import React from 'react';
import type { Station } from '../../types';
import type { MapLayerId } from '../../types/geospatial';
import { GeographicService } from '../../services/geographicService';

interface MapTooltipProps {
  station: Station | null;
  activeLayer: MapLayerId;
  selectedDate: string;
  isForecast?: boolean;
}

export const MapTooltip: React.FC<MapTooltipProps> = ({
  station,
  activeLayer,
  selectedDate,
  isForecast = false
}) => {
  if (!station) return null;

  // Retrieve authoritative observation for this station on this date
  const dayObs = GeographicService.getObservationsForDate(selectedDate)[station.station_id];
  // Retrieve forecast if in forecast mode
  const dayForecast = GeographicService.getForecastsForDate(selectedDate)[station.station_id];

  const elevInfo = GeographicService.getElevationCategory(station.elevation_m);

  return (
    <div style={{
      background: 'var(--chart-tooltip-bg)',
      backdropFilter: 'blur(12px)',
      border: '1px solid var(--border-base)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--space-3) var(--space-4)',
      boxShadow: 'var(--shadow-xl)',
      pointerEvents: 'none',
      minWidth: '240px',
      maxWidth: '320px',
      display: 'flex',
      flexDirection: 'column',
      gap: '4px',
      zIndex: 50
    }}>
      {/* Header with Station Name & Quality Badge */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px' }}>
        <div>
          <div style={{ fontSize: 'var(--font-sm)', fontWeight: 800, color: 'var(--text-primary)' }}>
            {station.station_name}
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--accent-primary)', marginTop: '1px' }}>
            {station.district}, {station.state}
          </div>
        </div>
        <span style={{
          fontSize: '9px',
          fontWeight: 700,
          padding: '2px 5px',
          borderRadius: '3px',
          background: isForecast ? 'var(--accent-warning)' : 'var(--accent-primary)',
          color: isForecast ? '#000' : '#fff',
          whiteSpace: 'nowrap'
        }}>
          {isForecast ? 'FORECAST' : dayObs?.rainfall === null ? 'DATA GAP' : 'OBSERVED'}
        </span>
      </div>

      {/* Coordinates & Elevation bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-2)',
        fontSize: '11px',
        color: 'var(--text-secondary)',
        borderTop: '1px solid var(--border-subtle)',
        paddingTop: '4px',
        marginTop: '2px'
      }}>
        <span>Elev: <b style={{ color: elevInfo.color }}>{station.elevation_m}m</b></span>
        <span>•</span>
        <span>Lat: {station.latitude.toFixed(2)}°</span>
        <span>Lon: {station.longitude.toFixed(2)}°</span>
      </div>

      {/* Layer-specific Telemetry Details */}
      <div style={{
        background: 'var(--bg-surface-elevated)',
        padding: 'var(--space-2)',
        borderRadius: 'var(--radius-sm)',
        marginTop: '2px',
        fontSize: 'var(--font-xs)',
        display: 'flex',
        flexDirection: 'column',
        gap: '3px'
      }}>
        {activeLayer === 'temperature' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-tertiary)' }}>Average Temp:</span>
              <b style={{ color: GeographicService.getTemperatureColor(dayObs?.avg_temp ?? null) }}>
                {dayObs?.avg_temp !== null && dayObs?.avg_temp !== undefined ? `${dayObs.avg_temp}°C` : 'N/A (Missing)'}
              </b>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px' }}>
              <span style={{ color: 'var(--text-tertiary)' }}>Min / Max:</span>
              <span>
                {dayObs?.min_temp !== null && dayObs?.min_temp !== undefined ? `${dayObs.min_temp}°C` : '—'} / {dayObs?.max_temp !== null && dayObs?.max_temp !== undefined ? `${dayObs.max_temp}°C` : '—'}
              </span>
            </div>
          </>
        )}

        {activeLayer === 'rainfall' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-tertiary)' }}>Precipitation:</span>
              <b>
                {dayObs?.rainfall === null || dayObs?.rainfall === undefined ? (
                  <span style={{ color: '#64748b', fontStyle: 'italic' }}>Missing (≠ 0mm)</span>
                ) : (
                  <span style={{ color: GeographicService.getIMDRainfallIntensity(dayObs.rainfall).color }}>
                    {dayObs.rainfall} mm
                  </span>
                )}
              </b>
            </div>
            {dayObs?.rainfall !== null && dayObs?.rainfall !== undefined && (
              <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>
                Classification: {GeographicService.getIMDRainfallIntensity(dayObs.rainfall).description}
              </div>
            )}
          </>
        )}

        {activeLayer === 'elevation' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-tertiary)' }}>Topography Tier:</span>
              <b style={{ color: elevInfo.color }}>{elevInfo.tier.replace('_', ' ')}</b>
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>
              {elevInfo.label}
            </div>
          </>
        )}

        {activeLayer === 'forecast_overlay' && dayForecast && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-tertiary)' }}>Predicted Temp:</span>
              <b style={{ color: GeographicService.getTemperatureColor(dayForecast.predicted_temp_c) }}>
                {dayForecast.predicted_temp_c}°C
              </b>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-tertiary)' }}>Expected Rain:</span>
              <b>{dayForecast.predicted_rainfall_mm} mm</b>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-tertiary)' }}>Rain Probability:</span>
              <b style={{
                color: dayForecast.predicted_rain_probability >= 0.5 ? 'var(--accent-warning)' : 'var(--accent-success)'
              }}>
                {(dayForecast.predicted_rain_probability * 100).toFixed(1)}%
              </b>
            </div>
            {dayForecast.actual_temp_c !== null && (
              <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', borderTop: '1px solid var(--border-subtle)', paddingTop: '2px', marginTop: '2px' }}>
                Actual holdout: {dayForecast.actual_temp_c}°C | {dayForecast.actual_rainfall_mm ?? 0} mm
              </div>
            )}
          </>
        )}

        {activeLayer === 'stations' && (
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px' }}>
            <span style={{ color: 'var(--text-tertiary)' }}>Historical Records:</span>
            <span>{station.record_count_modern_2021_2025.toLocaleString()} days (2021–2025)</span>
          </div>
        )}
      </div>

      {/* Date footer */}
      <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', textAlign: 'right' }}>
        Record Date: {selectedDate}
      </div>
    </div>
  );
};
