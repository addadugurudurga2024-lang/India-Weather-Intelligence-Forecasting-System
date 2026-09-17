import React from 'react';
import type { Station } from '../../types';
import type { MapLayerId, DailyStationObservationRecord, ForecastMapPoint } from '../../types/geospatial';
import { GeographicService } from '../../services/geographicService';

interface StationMarkerLayerProps {
  stations: Station[];
  activeLayer: MapLayerId;
  activeMetric?: string;
  selectedStationId: string | null;
  hoveredStationId: string | null;
  observations: Record<string, DailyStationObservationRecord>;
  forecasts: Record<string, ForecastMapPoint>;
  onSelectStation: (station: Station) => void;
  onHoverStation: (station: Station | null) => void;
  zoom: number;
}

export const StationMarkerLayer: React.FC<StationMarkerLayerProps> = ({
  stations,
  activeLayer,
  activeMetric,
  selectedStationId,
  hoveredStationId,
  observations,
  forecasts,
  onSelectStation,
  onHoverStation,
  zoom
}) => {
  // Compute marker radius based on zoom
  const baseRadius = Math.max(2.5, Math.min(6, 3.8 / Math.sqrt(zoom)));

  const getMarkerVisuals = (station: Station) => {
    const obs = observations[station.station_id];
    const forecast = forecasts[station.station_id];

    let color = 'var(--accent-primary)';
    let isMissing = false;

    if (activeLayer === 'temperature') {
      const temp = activeMetric === 'min_temp' ? obs?.min_temp : activeMetric === 'max_temp' ? obs?.max_temp : obs?.avg_temp;
      if (temp === null || temp === undefined) {
        color = '#64748b';
        isMissing = true;
      } else {
        color = GeographicService.getTemperatureColor(temp);
      }
    } else if (activeLayer === 'rainfall') {
      const rain = obs?.rainfall;
      if (rain === null || rain === undefined) {
        color = '#64748b'; // Explicit missing color (never 0)
        isMissing = true;
      } else if (activeMetric === 'is_rainy') {
        color = rain > 0 ? 'var(--accent-primary)' : '#94a3b8';
      } else {
        color = GeographicService.getIMDRainfallIntensity(rain).color;
      }
    } else if (activeLayer === 'elevation') {
      color = GeographicService.getElevationCategory(station.elevation_m).color;
    } else if (activeLayer === 'forecast_overlay') {
      if (!forecast) {
        color = '#64748b';
        isMissing = true;
      } else if (activeMetric === 'rain_probability') {
        const prob = forecast.predicted_rain_probability;
        if (prob >= 0.70) color = '#ef4444';
        else if (prob >= 0.50) color = '#f59e0b';
        else if (prob >= 0.35) color = '#38bdf8';
        else color = '#10b981';
      } else if (activeMetric === 'predicted_rainfall') {
        const rain = forecast.predicted_rainfall_mm;
        if (rain >= 35.5) color = '#ef4444';
        else if (rain >= 7.5) color = '#f59e0b';
        else if (rain >= 2.5) color = '#38bdf8';
        else color = '#94a3b8';
      } else {
        color = GeographicService.getTemperatureColor(forecast.predicted_temp_c);
      }
    }

    return { color, isMissing };
  };

  return (
    <g id="station-marker-layer">
      {stations.map((station) => {
        const { x, y } = GeographicService.projectCoordinates(station.latitude, station.longitude, 800, 720);
        const isSelected = selectedStationId === station.station_id;
        const isHovered = hoveredStationId === station.station_id;
        const { color, isMissing } = getMarkerVisuals(station);

        const r = isSelected ? baseRadius * 1.7 : isHovered ? baseRadius * 1.5 : baseRadius;

        return (
          <g
            key={station.station_id}
            onClick={(e) => {
              e.stopPropagation();
              onSelectStation(station);
            }}
            onMouseEnter={() => onHoverStation(station)}
            onMouseLeave={() => onHoverStation(null)}
            onFocus={() => onHoverStation(station)}
            onBlur={() => onHoverStation(null)}
            tabIndex={0}
            role="button"
            aria-label={`${station.station_name}, ${station.district}, ${station.state}`}
            style={{ cursor: 'pointer', outline: 'none' }}
          >
            {/* Pulsing beacon if station is currently selected */}
            {isSelected && (
              <circle
                cx={x}
                cy={y}
                r={baseRadius * 3}
                fill="none"
                stroke="var(--accent-warning)"
                strokeWidth={1.5}
                opacity={0.8}
              >
                <animate attributeName="r" values={`${baseRadius * 2};${baseRadius * 4.5};${baseRadius * 2}`} dur="2.2s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="0.9;0.15;0.9" dur="2.2s" repeatCount="indefinite" />
              </circle>
            )}

            {/* Hover halo */}
            {isHovered && !isSelected && (
              <circle
                cx={x}
                cy={y}
                r={baseRadius * 2.2}
                fill="none"
                stroke="var(--accent-primary)"
                strokeWidth={1.2}
                opacity={0.7}
              />
            )}

            {/* Main Station Marker Circle */}
            <circle
              cx={x}
              cy={y}
              r={r}
              fill={color}
              stroke={isSelected ? '#ffffff' : isHovered ? 'var(--text-primary)' : 'rgba(0,0,0,0.5)'}
              strokeWidth={isSelected || isHovered ? 1.8 : 0.8}
              strokeDasharray={isMissing ? '2 1.5' : undefined}
              opacity={isMissing ? 0.65 : 0.95}
            />
          </g>
        );
      })}
    </g>
  );
};
