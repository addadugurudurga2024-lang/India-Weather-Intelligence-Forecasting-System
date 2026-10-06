import React, { useState, useEffect } from 'react';
import { Search, Compass, Layers } from 'lucide-react';
import { stations } from '../data';
import { weatherService } from '../services';
import { useFilters } from '../context/FilterContext';
import { PreviewBanner } from '../components/common/PreviewBanner';
import { StationComparison } from '../components/stations/StationComparison';
import type { Station, WeatherObservation } from '../types';

export const StationsPage: React.FC = () => {
  const { filters, setScope } = useFilters();
  const [viewMode, setViewMode] = useState<'single' | 'compare'>('single');
  const [searchQuery, setSearchQuery] = useState('');
  const [localStationId, setLocalStationId] = useState<string>(stations[0]?.station_id || '');
  const [stationHistory, setStationHistory] = useState<WeatherObservation[]>([]);

  const activeStationId = (filters.stationId && filters.stationId !== 'ALL') ? filters.stationId : localStationId;
  const selectedStation = stations.find((s) => s.station_id === activeStationId) || stations[0];

  const stationId = selectedStation?.station_id;

  useEffect(() => {
    if (stationId) {
      setStationHistory([]); // Invalidate stale station history immediately
      weatherService.getStationHistory(stationId, 30).then(setStationHistory);
    }
  }, [stationId]);

  const filteredStations = stations.filter((s) => {
    if (filters.state !== 'ALL' && s.state !== filters.state) return false;
    if (filters.district !== 'ALL' && s.district !== filters.district) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        s.station_name.toLowerCase().includes(q) ||
        s.district.toLowerCase().includes(q) ||
        s.state.toLowerCase().includes(q) ||
        s.station_id.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const handleSelectStation = (station: Station) => {
    setLocalStationId(station.station_id);
    setScope(station.state, station.district, station.station_id);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <PreviewBanner
        message="Canonical Physical Station Explorer (413 Stations)"
        subtext="Reconciled during Phase 1.5 &amp; Phase 2.1: exactly 413 physical stations across 32 Indian States and Union Territories with 0 composite duplicate records."
      />

      {/* View Mode Switcher */}
      <div style={{ display: 'flex', gap: 'var(--space-2)', borderBottom: '1px solid var(--border-base)', paddingBottom: 'var(--space-3)' }}>
        <button
          className={`btn btn-sm ${viewMode === 'single' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setViewMode('single')}
        >
          <Compass size={15} />
          <span>Single Station Inspector</span>
        </button>
        <button
          className={`btn btn-sm ${viewMode === 'compare' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setViewMode('compare')}
        >
          <Layers size={15} />
          <span>Multi-Station Comparison (3–5 Stations)</span>
        </button>
      </div>

      {viewMode === 'compare' ? (
        <StationComparison />
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(320px, 400px) 1fr',
          gap: 'var(--space-6)',
          alignItems: 'start'
        }}>
        {/* Left Column: Search & Station Directory */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', maxHeight: '820px' }}>
          <div>
            <div style={{ fontSize: 'var(--font-lg)', fontWeight: 800, color: 'var(--text-primary)' }}>
              Physical Station Directory
            </div>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)' }}>
              Select a station to inspect physical geography and telemetry
            </div>
          </div>

          <div style={{ position: 'relative' }}>
            <input
              type="text"
              className="input"
              placeholder="Search 413 physical stations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ paddingLeft: '2.2rem' }}
            />
            <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)' }} />
          </div>

          <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-tertiary)', display: 'flex', justifyContent: 'space-between' }}>
            <span>Filtered: <b>{filteredStations.length}</b> / 413 stations</span>
            {filters.state !== 'ALL' && <span>State: {filters.state}</span>}
          </div>

          {/* Scrollable list */}
          <div style={{ overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', paddingRight: '4px' }}>
            {filteredStations.map((s) => {
              const isSelected = selectedStation?.station_id === s.station_id;
              return (
                <div
                  key={s.station_id}
                  onClick={() => handleSelectStation(s)}
                  style={{
                    padding: 'var(--space-3) var(--space-4)',
                    borderRadius: 'var(--radius-md)',
                    background: isSelected ? 'var(--accent-primary-subtle)' : 'var(--bg-surface-elevated)',
                    border: isSelected ? '1px solid var(--accent-primary)' : '1px solid var(--border-subtle)',
                    cursor: 'pointer',
                    transition: 'all var(--transition-fast)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontWeight: isSelected ? 700 : 600, fontSize: 'var(--font-sm)', color: isSelected ? 'var(--accent-primary)' : 'var(--text-primary)' }}>
                      {s.station_name}
                    </span>
                    <span className="badge badge-neutral">{s.state}</span>
                  </div>
                  <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)', marginTop: '2px' }}>
                    {s.district} • Elev: {s.elevation_m}m
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Selected Station Telemetry Card */}
        {selectedStation && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
            {/* Header Identity Card */}
            <div className="card" style={{
              background: 'linear-gradient(135deg, color-mix(in srgb, var(--accent-primary) 10%, var(--bg-surface)) 0%, var(--bg-surface) 100%)',
              border: '1px solid var(--border-base)',
              padding: 'var(--space-6)'
            }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'flex-start', justifyContent: 'space-between', gap: 'var(--space-4)' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
                    <span className="badge badge-primary">{selectedStation.state}</span>
                    <span className="badge badge-neutral">{selectedStation.district} District</span>
                    <span className="badge badge-success">IMD Canonical Record</span>
                  </div>
                  <div style={{ fontSize: 'var(--font-2xl)', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
                    {selectedStation.station_name}
                  </div>
                  <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>
                    ID: {selectedStation.station_id}
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)', textAlign: 'right' }}>
                  <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600 }}>Elevation</div>
                  <div style={{ fontSize: 'var(--font-2xl)', fontWeight: 800, color: 'var(--accent-primary)', fontFamily: 'var(--font-mono)' }}>
                    {selectedStation.elevation_m} <span style={{ fontSize: 'var(--font-sm)' }}>m</span>
                  </div>
                </div>
              </div>

              {/* Geographic Coordinates Capsule */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                gap: 'var(--space-4)',
                marginTop: 'var(--space-5)',
                borderTop: '1px solid var(--border-subtle)',
                paddingTop: 'var(--space-4)'
              }}>
                <div>
                  <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-tertiary)' }}>Latitude</div>
                  <div style={{ fontSize: 'var(--font-sm)', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
                    {selectedStation.latitude.toFixed(4)}° N
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-tertiary)' }}>Longitude</div>
                  <div style={{ fontSize: 'var(--font-sm)', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
                    {selectedStation.longitude.toFixed(4)}° E
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-tertiary)' }}>Operational Span</div>
                  <div style={{ fontSize: 'var(--font-sm)', fontWeight: 700, color: 'var(--text-primary)' }}>
                    {selectedStation.first_observed_date} → {selectedStation.last_observed_date}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-tertiary)' }}>Modern Days (2021-25)</div>
                  <div style={{ fontSize: 'var(--font-sm)', fontWeight: 700, color: 'var(--accent-success)', fontFamily: 'var(--font-mono)' }}>
                    {selectedStation.record_count_modern_2021_2025.toLocaleString()} / 1,502
                  </div>
                </div>
              </div>
            </div>

            {/* Station Recent Observation Table */}
            <div className="card" style={{ padding: 0 }}>
              <div style={{ padding: 'var(--space-4) var(--space-5)', borderBottom: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: 'var(--font-base)', fontWeight: 700, color: 'var(--text-primary)' }}>
                  Recent Observations for {selectedStation.station_name}
                </div>
                <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)' }}>
                  Canonical daily readings leading up to cutoff date (2025-02-10)
                </div>
              </div>

              <div className="data-table-container" style={{ border: 'none' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Avg Temp</th>
                      <th>Min / Max</th>
                      <th>Rainfall</th>
                      <th>Wind</th>
                      <th>Pressure</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stationHistory.length === 0 ? (
                      <tr>
                        <td colSpan={6} style={{ textAlign: 'center', padding: 'var(--space-6)', color: 'var(--text-tertiary)' }}>
                          No historical observation records found for this station.
                        </td>
                      </tr>
                    ) : (
                      stationHistory.slice(0, 15).map((obs) => (
                        <tr key={obs.date_of_record}>
                          <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{obs.date_of_record}</td>
                          <td style={{ fontWeight: 700, color: 'var(--accent-temp)' }}>{obs.avg_temp !== null ? `${obs.avg_temp}°C` : 'NaN'}</td>
                          <td style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)' }}>{obs.min_temp ?? '-'}° / {obs.max_temp ?? '-'}°</td>
                          <td>
                            {obs.rainfall === null ? (
                              <span className="badge badge-warning">Missing</span>
                            ) : obs.rainfall > 0 ? (
                              <span className="badge badge-rain">{obs.rainfall} mm</span>
                            ) : (
                              <span style={{ color: 'var(--text-tertiary)' }}>0.0 mm</span>
                            )}
                          </td>
                          <td style={{ fontFamily: 'var(--font-mono)' }}>{obs.wind_speed ?? '-'} km/h</td>
                          <td style={{ fontFamily: 'var(--font-mono)' }}>{obs.air_pressure ?? '-'} hPa</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
      )}
    </div>
  );
};
