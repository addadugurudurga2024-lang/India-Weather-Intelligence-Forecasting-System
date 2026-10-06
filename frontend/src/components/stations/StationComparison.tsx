import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Trash2, 
  RotateCcw, 
  Calendar, 
  TrendingUp,
  Layers
} from 'lucide-react';
import { stations } from '../../data';
import { weatherService, forecastService } from '../../services';
import type { Station, WeatherObservation, TimelineDayEntry } from '../../types';

interface StationComparisonProps {
  initialStationIds?: string[];
}

interface StationComparisonData {
  station: Station;
  d0Observation: WeatherObservation | null;
  recentHistory: WeatherObservation[];
  forecastHorizons: TimelineDayEntry[];
  forecastMode: string;
  isLoading: boolean;
  error: string | null;
}

const DEFAULT_STATION_IDS = [
  'rajahmundry_rjnagaram_17.1104_81.8182_46m',
  'new_delhi_safdarjung_28.5833_77.2000_211m',
  'madras_13.0667_80.2500_6m'
];

const MAX_STATIONS = 5;
const MIN_STATIONS = 1;

export const StationComparison: React.FC<StationComparisonProps> = ({
  initialStationIds = DEFAULT_STATION_IDS
}) => {
  const [selectedIds, setSelectedIds] = useState<string[]>(initialStationIds);
  const [comparisonData, setComparisonData] = useState<Record<string, StationComparisonData>>({});
  const [selectedAddStationId, setSelectedAddStationId] = useState<string>('');
  const [forecastMode, setForecastMode] = useState<'operational_current' | 'historical_holdout_replay'>('operational_current');
  const [expandedHorizonStation, setExpandedHorizonStation] = useState<string | null>(null);

  // Fetch station data whenever selected IDs or mode change
  useEffect(() => {
    selectedIds.forEach((id) => {
      const stn = stations.find((s) => s.station_id === id);
      if (!stn) return;

      setComparisonData((prev) => ({
        ...prev,
        [id]: {
          station: stn,
          d0Observation: prev[id]?.d0Observation || null,
          recentHistory: prev[id]?.recentHistory || [],
          forecastHorizons: prev[id]?.forecastHorizons || [],
          forecastMode,
          isLoading: true,
          error: null
        }
      }));

      // Fetch history and timeline in parallel
      Promise.all([
        weatherService.getStationHistory(id, 5),
        forecastService.get25DayTimeline(id, forecastMode)
      ])
        .then(([history, timelinePayload]) => {
          const forecasts = (timelinePayload?.timeline?.filter((d: TimelineDayEntry) => d.relative_day > 0) || []).slice(0, 12);
          
          setComparisonData((prev) => ({
            ...prev,
            [id]: {
              station: stn,
              d0Observation: history.length > 0 ? history[0] : null,
              recentHistory: history,
              forecastHorizons: forecasts,
              forecastMode,
              isLoading: false,
              error: null
            }
          }));
        })
        .catch((err) => {
          setComparisonData((prev) => ({
            ...prev,
            [id]: {
              station: stn,
              d0Observation: null,
              recentHistory: [],
              forecastHorizons: [],
              forecastMode,
              isLoading: false,
              error: err?.message || 'Failed to retrieve canonical station telemetry'
            }
          }));
        });
    });
  }, [selectedIds, forecastMode]);

  const handleAddStation = () => {
    if (!selectedAddStationId) return;
    if (selectedIds.length >= MAX_STATIONS) return;
    if (selectedIds.includes(selectedAddStationId)) return;

    setSelectedIds((prev) => [...prev, selectedAddStationId]);
    setSelectedAddStationId('');
  };

  const handleRemoveStation = (id: string) => {
    if (selectedIds.length <= MIN_STATIONS) return;
    setSelectedIds((prev) => prev.filter((sId) => sId !== id));
    setComparisonData((prev) => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
  };

  const handleReset = () => {
    setSelectedIds(DEFAULT_STATION_IDS);
  };

  const availableStations = stations
    .filter((s) => !selectedIds.includes(s.station_id))
    .sort((a, b) => a.station_name.localeCompare(b.station_name));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Comparison Control Toolbar */}
      <div className="card" style={{ padding: 'var(--space-4)' }}>
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 'var(--space-4)'
        }}>
          <div>
            <div style={{ fontSize: 'var(--font-lg)', fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <Layers size={20} style={{ color: 'var(--accent-primary)' }} />
              <span>Multi-Station Comparative Intelligence</span>
              <span className="badge badge-primary">{selectedIds.length} / {MAX_STATIONS} Active</span>
            </div>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Compare physical coordinates, current D0 observations, historical baselines, and multi-horizon operational forecasts side-by-side.
            </div>
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 'var(--space-3)' }}>
            {/* Forecast Mode Selector */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 700 }}>Mode:</span>
              <select
                className="select"
                value={forecastMode}
                onChange={(e) => setForecastMode(e.target.value as any)}
                style={{ fontSize: 'var(--font-xs)', padding: '4px 8px', height: '32px' }}
                aria-label="Comparison Forecast Mode"
              >
                <option value="operational_current">Current Operational Ingestion (Dynamic D0)</option>
                <option value="historical_holdout_replay">Audited Ground-Truth Replay (2025-01-20)</option>
              </select>
            </div>

            {/* Add Station Dropdown */}
            {selectedIds.length < MAX_STATIONS ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <select
                  className="select"
                  value={selectedAddStationId}
                  onChange={(e) => setSelectedAddStationId(e.target.value)}
                  style={{ fontSize: 'var(--font-xs)', minWidth: '220px', height: '32px' }}
                  aria-label="Add station to comparison"
                >
                  <option value="">+ Add Station ({availableStations.length} available)...</option>
                  {availableStations.map((s) => (
                    <option key={s.station_id} value={s.station_id}>
                      {s.station_name} ({s.state} • {s.district})
                    </option>
                  ))}
                </select>
                <button
                  className="btn btn-primary btn-sm"
                  onClick={handleAddStation}
                  disabled={!selectedAddStationId}
                  title="Add selected station to comparison"
                  style={{ height: '32px' }}
                >
                  <Plus size={14} />
                  <span>Add</span>
                </button>
              </div>
            ) : (
              <span className="badge badge-warning" title="Maximum 5 stations allowed for focused comparison">
                Max 5 Stations Reached
              </span>
            )}

            {/* Reset Defaults */}
            <button
              className="btn btn-secondary btn-sm"
              onClick={handleReset}
              title="Reset comparison to default 3 stations"
              style={{ height: '32px' }}
            >
              <RotateCcw size={14} />
              <span>Reset</span>
            </button>
          </div>
        </div>
      </div>

      {/* Cross-Station Macro Comparison Grid (Side-by-Side Summary Cards) */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${selectedIds.length}, minmax(300px, 1fr))`,
        gap: 'var(--space-4)',
        overflowX: 'auto',
        paddingBottom: 'var(--space-2)'
      }}>
        {selectedIds.map((id) => {
          const item = comparisonData[id];
          const stn = item?.station || stations.find((s) => s.station_id === id);
          if (!stn) return null;

          const h1 = item?.forecastHorizons?.[0];
          const h7 = item?.forecastHorizons?.[6];
          const d0Obs = item?.d0Observation;
          const isExpanded = expandedHorizonStation === id;

          return (
            <div
              key={id}
              className="card"
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--space-4)',
                borderTop: '4px solid var(--accent-primary)',
                minWidth: '320px',
                background: 'var(--bg-surface)'
              }}
            >
              {/* Card Header & Identity */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-subtle)', paddingBottom: 'var(--space-3)' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                    <span className="badge badge-primary">{stn.state}</span>
                    <span className="badge badge-neutral">{stn.district}</span>
                  </div>
                  <div style={{ fontSize: 'var(--font-lg)', fontWeight: 800, color: 'var(--text-primary)' }}>
                    {stn.station_name}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>
                    {stn.station_id}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {selectedIds.length > MIN_STATIONS && (
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleRemoveStation(id)}
                      title={`Remove ${stn.station_name} from comparison`}
                      style={{ padding: '4px 6px', height: '26px' }}
                    >
                      <Trash2 size={13} />
                    </button>
                  )}
                </div>
              </div>

              {/* Geographic Telemetry Capsule */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: 'var(--space-2)',
                background: 'var(--bg-surface-elevated)',
                padding: 'var(--space-2) var(--space-3)',
                borderRadius: 'var(--radius-sm)',
                textAlign: 'center'
              }}>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Latitude</div>
                  <div style={{ fontSize: 'var(--font-xs)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{stn.latitude.toFixed(2)}°N</div>
                </div>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Longitude</div>
                  <div style={{ fontSize: 'var(--font-xs)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{stn.longitude.toFixed(2)}°E</div>
                </div>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Elevation</div>
                  <div style={{ fontSize: 'var(--font-xs)', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--accent-primary)' }}>{stn.elevation_m}m</div>
                </div>
              </div>

              {/* Section 1: Current D0 Telemetry */}
              <div style={{ border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: 'var(--space-3)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Calendar size={13} style={{ color: 'var(--accent-primary)' }} />
                    D0 Telemetry ({forecastMode === 'historical_holdout_replay' ? '2025-01-20' : 'Dynamic Current'})
                  </span>
                  <span className="badge badge-success" style={{ fontSize: '10px' }}>
                    {d0Obs ? 'OBSERVED' : 'CANONICAL'}
                  </span>
                </div>

                {d0Obs ? (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
                    <div>
                      <div style={{ fontSize: '10px', color: 'var(--text-tertiary)' }}>Avg Temp</div>
                      <div style={{ fontSize: 'var(--font-base)', fontWeight: 800, color: 'var(--accent-temp)' }}>
                        {d0Obs.avg_temp !== null ? `${d0Obs.avg_temp}°C` : '--'}
                      </div>
                      <div style={{ fontSize: '10px', color: 'var(--text-tertiary)' }}>
                        {d0Obs.min_temp ?? '-'}° / {d0Obs.max_temp ?? '-'}°
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: '10px', color: 'var(--text-tertiary)' }}>Rainfall</div>
                      <div style={{ fontSize: 'var(--font-base)', fontWeight: 800, color: d0Obs.rainfall && d0Obs.rainfall > 0 ? 'var(--accent-rain)' : 'var(--text-primary)' }}>
                        {d0Obs.rainfall !== null ? `${d0Obs.rainfall} mm` : '--'}
                      </div>
                      <div style={{ fontSize: '10px', color: 'var(--text-tertiary)' }}>
                        {d0Obs.rainfall === 0 ? 'Verified Dry Day' : d0Obs.rainfall ? 'Rain Event' : 'Missing Gauge'}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: '10px', color: 'var(--text-tertiary)' }}>Wind Speed</div>
                      <div style={{ fontSize: 'var(--font-xs)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                        {d0Obs.wind_speed !== null ? `${d0Obs.wind_speed} km/h` : '--'}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: '10px', color: 'var(--text-tertiary)' }}>Air Pressure</div>
                      <div style={{ fontSize: 'var(--font-xs)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                        {d0Obs.air_pressure !== null ? `${d0Obs.air_pressure} hPa` : '--'}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)', textAlign: 'center', padding: 'var(--space-2)' }}>
                    Loading canonical observation...
                  </div>
                )}
              </div>

              {/* Section 2: Recent Historical Ground Truth (Last 3 records) */}
              <div style={{ border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: 'var(--space-3)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-primary)' }}>
                    Recent Historical Records
                  </span>
                  <span style={{ fontSize: '10px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>
                    Cutoff: {stn.last_observed_date}
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {item?.recentHistory?.slice(0, 3).map((obs) => (
                    <div
                      key={obs.date_of_record}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        fontSize: '11px',
                        padding: '3px 6px',
                        background: 'var(--bg-surface-elevated)',
                        borderRadius: 'var(--radius-xs)',
                        fontFamily: 'var(--font-mono)'
                      }}
                    >
                      <span style={{ color: 'var(--text-secondary)' }}>{obs.date_of_record}</span>
                      <span style={{ fontWeight: 700, color: 'var(--accent-temp)' }}>{obs.avg_temp !== null ? `${obs.avg_temp}°C` : '--'}</span>
                      <span style={{ color: obs.rainfall && obs.rainfall > 0 ? 'var(--accent-rain)' : 'var(--text-tertiary)' }}>
                        {obs.rainfall !== null ? `${obs.rainfall}mm` : '--'}
                      </span>
                    </div>
                  ))}
                  {(!item?.recentHistory || item.recentHistory.length === 0) && (
                    <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', textAlign: 'center' }}>
                      No canonical records returned
                    </div>
                  )}
                </div>
              </div>

              {/* Section 3: Operational Multi-Horizon Forecast Preview */}
              <div style={{ border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: 'var(--space-3)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <TrendingUp size={13} style={{ color: 'var(--accent-primary)' }} />
                    12-Day Operational Forecast
                  </span>
                  <span className="badge badge-info" style={{ fontSize: '10px' }}>
                    XGBoost Multi-Horizon
                  </span>
                </div>

                {item?.forecastHorizons && item.forecastHorizons.length > 0 ? (
                  <div>
                    {/* Horizon Highlights: D+1 (H1) and D+7 (H7) */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', marginBottom: '8px' }}>
                      {h1 && (
                        <div style={{ background: 'var(--bg-surface-elevated)', padding: '6px 8px', borderRadius: 'var(--radius-sm)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-tertiary)' }}>
                            <span style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>D+1 (H1)</span>
                            <span>{h1.date}</span>
                          </div>
                          <div style={{ fontSize: 'var(--font-sm)', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>
                            {h1.temperature_avg !== null ? `${h1.temperature_avg}°C` : '--'}
                          </div>
                          <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>
                            PoP: {h1.rain_probability !== null ? `${Math.round(h1.rain_probability * 100)}%` : '--'} • {h1.rainfall_amount ?? 0}mm
                          </div>
                        </div>
                      )}
                      {h7 && (
                        <div style={{ background: 'var(--bg-surface-elevated)', padding: '6px 8px', borderRadius: 'var(--radius-sm)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-tertiary)' }}>
                            <span style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>D+7 (H7)</span>
                            <span>{h7.date}</span>
                          </div>
                          <div style={{ fontSize: 'var(--font-sm)', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>
                            {h7.temperature_avg !== null ? `${h7.temperature_avg}°C` : '--'}
                          </div>
                          <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>
                            PoP: {h7.rain_probability !== null ? `${Math.round(h7.rain_probability * 100)}%` : '--'} • {h7.rainfall_amount ?? 0}mm
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Toggle Detailed 12-Horizon Matrix */}
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => setExpandedHorizonStation(isExpanded ? null : id)}
                      style={{ width: '100%', fontSize: '11px', padding: '4px' }}
                    >
                      {isExpanded ? '▲ Collapse 12-Horizon Table' : '▼ Expand Full D+1..D+12 Forecast Table'}
                    </button>

                    {isExpanded && (
                      <div style={{ marginTop: '8px', maxHeight: '240px', overflowY: 'auto' }}>
                        <table style={{ width: '100%', fontSize: '10px', borderCollapse: 'collapse', textAlign: 'left', fontFamily: 'var(--font-mono)' }}>
                          <thead>
                            <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-tertiary)' }}>
                              <th style={{ padding: '3px 2px' }}>H</th>
                              <th style={{ padding: '3px 2px' }}>Target</th>
                              <th style={{ padding: '3px 2px' }}>Tavg</th>
                              <th style={{ padding: '3px 2px' }}>Tmin/Max</th>
                              <th style={{ padding: '3px 2px' }}>PoP</th>
                              <th style={{ padding: '3px 2px' }}>Rain</th>
                            </tr>
                          </thead>
                          <tbody>
                            {item.forecastHorizons.map((h) => (
                              <tr key={h.relative_day} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                                <td style={{ padding: '3px 2px', fontWeight: 700, color: 'var(--accent-primary)' }}>D+{h.relative_day}</td>
                                <td style={{ padding: '3px 2px', color: 'var(--text-secondary)' }}>{h.date.slice(5)}</td>
                                <td style={{ padding: '3px 2px', fontWeight: 700, color: 'var(--accent-temp)' }}>{h.temperature_avg}°</td>
                                <td style={{ padding: '3px 2px', color: 'var(--text-tertiary)' }}>{h.temperature_min}°/{h.temperature_max}°</td>
                                <td style={{ padding: '3px 2px' }}>{h.rain_probability !== null ? `${Math.round(h.rain_probability * 100)}%` : '-'}</td>
                                <td style={{ padding: '3px 2px', color: h.rainfall_amount && h.rainfall_amount > 0 ? 'var(--accent-rain)' : 'var(--text-tertiary)' }}>
                                  {h.rainfall_amount ?? 0}mm
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                ) : (
                  <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', textAlign: 'center', padding: 'var(--space-2)' }}>
                    Loading operational forecast models...
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
