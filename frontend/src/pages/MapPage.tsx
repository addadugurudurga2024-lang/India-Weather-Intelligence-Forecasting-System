import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MapPin,
  Compass,
  Layers,
  ArrowRight,
  Info,
  Calendar,
  Zap,
  BarChart2
} from 'lucide-react';
import { IndiaMapCanvas } from '../components/maps/IndiaMapCanvas';
import { GlobalFilterBar } from '../components/filters/GlobalFilterBar';
import { stations } from '../data';
import { useFilters } from '../context/FilterContext';
import { GeographicService } from '../services/geographicService';

export const MapPage: React.FC = () => {
  const { filters } = useFilters();
  const navigate = useNavigate();

  const selectedStation = filters.stationId !== 'ALL'
    ? stations.find((s) => s.station_id === filters.stationId)
    : null;

  const stateAggregates = filters.state !== 'ALL'
    ? GeographicService.getStateAggregates(filters.state)
    : null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <h1 style={{ fontSize: 'var(--font-2xl)', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
              Geospatial Telemetry & Forecast Intelligence
            </h1>
            <span className="badge badge-primary" style={{ fontSize: '11px' }}>
              Phase 5 Active
            </span>
          </div>
          <div style={{ fontSize: 'var(--font-sm)', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Multi-layer interactive geospatial mapping across all 413 canonical physical stations with authoritative 2025 observations and Phase 3 XGBoost holdout predictions.
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <span className="badge badge-neutral" style={{ padding: '6px 12px' }}>
            <Compass size={13} style={{ marginRight: '6px', color: 'var(--accent-primary)' }} />
            413 Canonical Stations
          </span>
          <span className="badge badge-neutral" style={{ padding: '6px 12px' }}>
            <Calendar size={13} style={{ marginRight: '6px', color: 'var(--accent-primary)' }} />
            41 Modern Dates (2025)
          </span>
        </div>
      </div>

      {/* Global Filter Bar */}
      <GlobalFilterBar />

      {/* Primary Interactive Map Canvas */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
        <IndiaMapCanvas
          stations={stations}
          height={700}
        />
      </div>

      {/* Contextual Intelligence Drawer (Station or State Selection Details) */}
      {(selectedStation || stateAggregates) && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: selectedStation && stateAggregates ? '1fr 1fr' : '1fr',
          gap: 'var(--space-4)'
        }}>
          {/* Selected Station Deep Telemetry Card */}
          {selectedStation && (
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  <div style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--accent-primary-subtle)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--accent-primary)'
                  }}>
                    <MapPin size={18} />
                  </div>
                  <div>
                    <div style={{ fontSize: 'var(--font-base)', fontWeight: 800, color: 'var(--text-primary)' }}>
                      {selectedStation.station_name}
                    </div>
                    <div style={{ fontSize: 'var(--font-xs)', color: 'var(--accent-primary)' }}>
                      {selectedStation.district}, {selectedStation.state}
                    </div>
                  </div>
                </div>
                <span className="badge badge-warning">Selected Focus</span>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: 'var(--space-2)',
                background: 'var(--bg-surface-elevated)',
                padding: 'var(--space-3)',
                borderRadius: 'var(--radius-md)',
                fontSize: 'var(--font-xs)'
              }}>
                <div>
                  <div style={{ color: 'var(--text-tertiary)', fontSize: '10px' }}>ELEVATION</div>
                  <div style={{ fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>
                    {selectedStation.elevation_m} meters
                  </div>
                </div>
                <div>
                  <div style={{ color: 'var(--text-tertiary)', fontSize: '10px' }}>COORDINATES</div>
                  <div style={{ fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>
                    {selectedStation.latitude.toFixed(2)}°N, {selectedStation.longitude.toFixed(2)}°E
                  </div>
                </div>
                <div>
                  <div style={{ color: 'var(--text-tertiary)', fontSize: '10px' }}>RECORD DENSITY</div>
                  <div style={{ fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>
                    {selectedStation.record_count_modern_2021_2025.toLocaleString()} days
                  </div>
                </div>
              </div>

              {/* Station Deep-dive Navigation Links */}
              <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
                <button
                  onClick={() => navigate('/stations')}
                  className="btn btn-primary"
                  style={{ fontSize: 'var(--font-xs)', display: 'flex', alignItems: 'center', gap: '6px' }}
                >
                  <span>View in Station Explorer</span>
                  <ArrowRight size={14} />
                </button>
                <button
                  onClick={() => navigate('/analytics')}
                  className="btn btn-secondary"
                  style={{ fontSize: 'var(--font-xs)', display: 'flex', alignItems: 'center', gap: '6px' }}
                >
                  <BarChart2 size={14} />
                  <span>Station Analytics</span>
                </button>
                <button
                  onClick={() => navigate('/forecast')}
                  className="btn btn-secondary"
                  style={{ fontSize: 'var(--font-xs)', display: 'flex', alignItems: 'center', gap: '6px' }}
                >
                  <Zap size={14} />
                  <span>Forecast Models</span>
                </button>
              </div>
            </div>
          )}

          {/* Selected State Derived Aggregate Card */}
          {stateAggregates && (
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  <div style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: 'var(--radius-md)',
                    background: 'rgba(52, 211, 153, 0.15)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#34d399'
                  }}>
                    <Layers size={18} />
                  </div>
                  <div>
                    <div style={{ fontSize: 'var(--font-base)', fontWeight: 800, color: 'var(--text-primary)' }}>
                      {stateAggregates.stateName} Regional Profile
                    </div>
                    <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)' }}>
                      Derived spatial summary across all monitored districts
                    </div>
                  </div>
                </div>
                <span className="badge badge-neutral">State Aggregate</span>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: 'var(--space-2)',
                background: 'var(--bg-surface-elevated)',
                padding: 'var(--space-3)',
                borderRadius: 'var(--radius-md)',
                fontSize: 'var(--font-xs)'
              }}>
                <div>
                  <div style={{ color: 'var(--text-tertiary)', fontSize: '10px' }}>TOTAL STATIONS</div>
                  <div style={{ fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>
                    {stateAggregates.stationCount} stations
                  </div>
                </div>
                <div>
                  <div style={{ color: 'var(--text-tertiary)', fontSize: '10px' }}>AVG ELEVATION</div>
                  <div style={{ fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>
                    {stateAggregates.avgElevation} m
                  </div>
                </div>
                <div>
                  <div style={{ color: 'var(--text-tertiary)', fontSize: '10px' }}>STATE MEAN TEMP</div>
                  <div style={{ fontWeight: 800, color: 'var(--accent-primary)', marginTop: '2px' }}>
                    {stateAggregates.avgTemp !== null ? `${stateAggregates.avgTemp}°C` : 'N/A'}
                  </div>
                </div>
                <div>
                  <div style={{ color: 'var(--text-tertiary)', fontSize: '10px' }}>AVG RAINFALL</div>
                  <div style={{ fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>
                    {stateAggregates.avgRainfall !== null ? `${stateAggregates.avgRainfall} mm` : 'N/A'}
                  </div>
                </div>
              </div>

              <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Info size={12} />
                <span>Derived spatial aggregate. Never represent state aggregates as direct physical station readings.</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
