import React, { useState } from 'react';
import { X, ArrowRightLeft, MapPin, Mountain, Thermometer, CloudRain, Zap, Plus, Trash2 } from 'lucide-react';
import type { Station } from '../../types';
import { GeographicService } from '../../services/geographicService';

interface GeographicComparisonModalProps {
  isOpen: boolean;
  onClose: () => void;
  stations: Station[];
  initialStationIds: string[];
  selectedDate: string;
}

export const GeographicComparisonModal: React.FC<GeographicComparisonModalProps> = ({
  isOpen,
  onClose,
  stations,
  initialStationIds,
  selectedDate
}) => {
  const [selectedIds, setSelectedIds] = useState<string[]>(
    initialStationIds.length > 0 ? initialStationIds.slice(0, 3) : [stations[0]?.station_id, stations[1]?.station_id].filter(Boolean)
  );
  const [candidateId, setCandidateId] = useState<string>('');

  if (!isOpen) return null;

  const comparedStations = selectedIds
    .map((id) => stations.find((s) => s.station_id === id))
    .filter(Boolean) as Station[];

  const handleAddStation = () => {
    if (candidateId && !selectedIds.includes(candidateId) && selectedIds.length < 3) {
      setSelectedIds([...selectedIds, candidateId]);
      setCandidateId('');
    }
  };

  const handleRemoveStation = (id: string) => {
    setSelectedIds(selectedIds.filter((sId) => sId !== id));
  };

  const obsForDate = GeographicService.getObservationsForDate(selectedDate);
  const forecastForDate = GeographicService.getForecastsForDate(selectedDate);

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(6px)',
      zIndex: 100,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 'var(--space-4)'
    }}>
      <div style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border-base)',
        borderRadius: 'var(--radius-xl)',
        boxShadow: 'var(--shadow-xl)',
        width: '100%',
        maxWidth: '960px',
        maxHeight: '90vh',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-4)',
        padding: 'var(--space-6)'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--accent-primary-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-primary)'
            }}>
              <ArrowRightLeft size={22} />
            </div>
            <div>
              <div style={{ fontSize: 'var(--font-lg)', fontWeight: 800, color: 'var(--text-primary)' }}>
                Multi-Location Geospatial Comparison
              </div>
              <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)' }}>
                Side-by-side analysis of elevation, observed telemetry, and Phase 3 holdout forecasts for {selectedDate}.
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="btn btn-ghost btn-icon"
            aria-label="Close comparison modal"
          >
            <X size={20} />
          </button>
        </div>

        {/* Add Station Selector */}
        {selectedIds.length < 3 && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-2)',
            background: 'var(--bg-surface-elevated)',
            padding: 'var(--space-3)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)'
          }}>
            <select
              value={candidateId}
              onChange={(e) => setCandidateId(e.target.value)}
              className="select"
              style={{ flex: 1, fontSize: 'var(--font-xs)' }}
            >
              <option value="">-- Select a station to add to comparison (max 3) --</option>
              {stations
                .filter((s) => !selectedIds.includes(s.station_id))
                .map((s) => (
                  <option key={s.station_id} value={s.station_id}>
                    {s.station_name} ({s.district}, {s.state}) — {s.elevation_m}m
                  </option>
                ))}
            </select>
            <button
              onClick={handleAddStation}
              disabled={!candidateId}
              className="btn btn-primary"
              style={{ fontSize: 'var(--font-xs)', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <Plus size={14} /> Add Location
            </button>
          </div>
        )}

        {/* Comparison Columns Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${comparedStations.length}, 1fr)`,
          gap: 'var(--space-4)',
          overflowX: 'auto'
        }}>
          {comparedStations.map((station) => {
            const obs = obsForDate[station.station_id];
            const forecast = forecastForDate[station.station_id];
            const elev = GeographicService.getElevationCategory(station.elevation_m);

            return (
              <div
                key={station.station_id}
                className="card"
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 'var(--space-3)',
                  position: 'relative'
                }}
              >
                {/* Station Card Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontSize: 'var(--font-base)', fontWeight: 800, color: 'var(--text-primary)' }}>
                      {station.station_name}
                    </div>
                    <div style={{ fontSize: 'var(--font-xs)', color: 'var(--accent-primary)', marginTop: '2px' }}>
                      {station.district}, {station.state}
                    </div>
                  </div>
                  {comparedStations.length > 1 && (
                    <button
                      onClick={() => handleRemoveStation(station.station_id)}
                      className="btn btn-ghost btn-icon"
                      style={{ color: 'var(--accent-danger)', padding: '4px' }}
                      title="Remove station from comparison"
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>

                {/* Geography Section */}
                <div style={{
                  background: 'var(--bg-surface-elevated)',
                  padding: 'var(--space-3)',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                  fontSize: 'var(--font-xs)'
                }}>
                  <div style={{ fontWeight: 700, color: 'var(--text-tertiary)', textTransform: 'uppercase', fontSize: '10px' }}>
                    Geographic Profile
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Mountain size={13} /> Elevation:</span>
                    <b style={{ color: elev.color }}>{station.elevation_m} m ({elev.tier})</b>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><MapPin size={13} /> Coordinates:</span>
                    <span>{station.latitude.toFixed(2)}°N, {station.longitude.toFixed(2)}°E</span>
                  </div>
                </div>

                {/* Telemetry Observation Section */}
                <div style={{
                  background: 'var(--bg-surface-elevated)',
                  padding: 'var(--space-3)',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                  fontSize: 'var(--font-xs)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 700, color: 'var(--text-tertiary)', textTransform: 'uppercase', fontSize: '10px' }}>
                      Observed Telemetry ({selectedDate})
                    </span>
                    <span className="badge badge-primary" style={{ fontSize: '9px' }}>OBSERVED</span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Thermometer size={13} /> Avg Temp:</span>
                    <b>{obs?.avg_temp !== null && obs?.avg_temp !== undefined ? `${obs.avg_temp}°C` : 'N/A (Missing)'}</b>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Min / Max Temp:</span>
                    <span>{obs?.min_temp ?? '—'}°C / {obs?.max_temp ?? '—'}°C</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><CloudRain size={13} /> Rainfall:</span>
                    <b>
                      {obs?.rainfall === null || obs?.rainfall === undefined ? (
                        <span style={{ color: '#64748b', fontStyle: 'italic' }}>Missing Observation</span>
                      ) : (
                        `${obs.rainfall} mm`
                      )}
                    </b>
                  </div>
                </div>

                {/* XGBoost Holdout Forecast Section */}
                <div style={{
                  background: 'var(--bg-surface-elevated)',
                  padding: 'var(--space-3)',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                  fontSize: 'var(--font-xs)',
                  border: '1px solid rgba(245, 158, 11, 0.2)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 700, color: 'var(--accent-warning)', textTransform: 'uppercase', fontSize: '10px' }}>
                      Next-Day Holdout Forecast
                    </span>
                    <span className="badge badge-warning" style={{ fontSize: '9px', display: 'flex', alignItems: 'center', gap: '3px' }}>
                      <Zap size={9} /> XGBoost
                    </span>
                  </div>

                  {forecast ? (
                    <>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Predicted Temp:</span>
                        <b style={{ color: GeographicService.getTemperatureColor(forecast.predicted_temp_c) }}>
                          {forecast.predicted_temp_c}°C
                        </b>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Predicted Rainfall:</span>
                        <b>{forecast.predicted_rainfall_mm} mm</b>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Rain Probability:</span>
                        <b style={{ color: forecast.predicted_rain_probability >= 0.5 ? 'var(--accent-warning)' : 'var(--accent-success)' }}>
                          {(forecast.predicted_rain_probability * 100).toFixed(1)}%
                        </b>
                      </div>
                      <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', borderTop: '1px solid var(--border-subtle)', paddingTop: '3px' }}>
                        Validation Error (Temp): {forecast.actual_temp_c !== null && forecast.actual_temp_c !== undefined ? `${Math.abs(forecast.predicted_temp_c - forecast.actual_temp_c).toFixed(2)}°C` : 'N/A'}
                      </div>
                    </>
                  ) : (
                    <div style={{ color: 'var(--text-tertiary)', fontStyle: 'italic', fontSize: '11px' }}>
                      No forecast record for this date
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Scientific Disclaimer Footer */}
        <div style={{
          background: 'var(--bg-surface-elevated)',
          padding: 'var(--space-3) var(--space-4)',
          borderRadius: 'var(--radius-md)',
          fontSize: '11px',
          color: 'var(--text-tertiary)',
          borderLeft: '3px solid var(--accent-primary)'
        }}>
          <b>Scientific Notice:</b> Geographic comparisons illustrate spatial and altitudinal gradients across agro-climatic zones. Simple spatial comparisons do not imply direct causal relationships between parameters.
        </div>
      </div>
    </div>
  );
};
