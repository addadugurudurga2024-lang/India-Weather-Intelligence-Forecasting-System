import React, { useState, useMemo } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, MapPin, Layers } from 'lucide-react';
import type { Station } from '../../types';
import { useFilters } from '../../context/FilterContext';

interface IndiaStationMapProps {
  stations: Station[];
  onSelectStation?: (station: Station) => void;
  height?: number;
}

export const IndiaStationMap: React.FC<IndiaStationMapProps> = ({
  stations,
  onSelectStation,
  height = 560
}) => {
  const { filters, setScope } = useFilters();
  const [zoom, setZoom] = useState(1);
  const [hoveredStation, setHoveredStation] = useState<Station | null>(null);
  const [colorMode, setColorMode] = useState<'elevation' | 'state'>('elevation');

  // Coordinate bounding box for India
  const bounds = {
    minLat: 6.5,
    maxLat: 36.5,
    minLon: 68.0,
    maxLon: 97.5
  };

  const mapWidth = 800;
  const mapHeight = 720;

  // Project lat/lon to SVG coordinates
  const project = (lat: number, lon: number) => {
    const x = ((lon - bounds.minLon) / (bounds.maxLon - bounds.minLon)) * mapWidth;
    const y = ((bounds.maxLat - lat) / (bounds.maxLat - bounds.minLat)) * mapHeight;
    return { x, y };
  };

  const filteredStations = useMemo(() => {
    return stations.filter((s) => {
      if (filters.state !== 'ALL' && s.state !== filters.state) return false;
      if (filters.district !== 'ALL' && s.district !== filters.district) return false;
      return true;
    });
  }, [stations, filters]);

  const handleStationClick = (station: Station) => {
    setScope(station.state, station.district, station.station_id);
    if (onSelectStation) onSelectStation(station);
  };

  const getStationColor = (station: Station) => {
    if (filters.stationId === station.station_id) return 'var(--accent-warning)';
    if (colorMode === 'elevation') {
      if (station.elevation_m > 1500) return '#c084fc'; // High Himalayan
      if (station.elevation_m > 600) return '#38bdf8';  // Plateau
      if (station.elevation_m > 150) return '#34d399';  // Plains
      return '#38bdf8'; // Coastal
    }
    return 'var(--accent-primary)';
  };

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden', position: 'relative', height }}>
      {/* Map Header Toolbar */}
      <div style={{
        position: 'absolute',
        top: 'var(--space-3)',
        left: 'var(--space-3)',
        zIndex: 10,
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-2)',
        background: 'var(--bg-surface-glass)',
        backdropFilter: 'blur(8px)',
        padding: 'var(--space-2) var(--space-3)',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)',
        fontSize: 'var(--font-xs)',
        color: 'var(--text-secondary)'
      }}>
        <MapPin size={15} style={{ color: 'var(--accent-primary)' }} />
        <span><b>{filteredStations.length}</b> Stations Rendered</span>
        {filters.state !== 'ALL' && <span className="badge badge-neutral">{filters.state}</span>}
      </div>

      {/* Map Control Buttons */}
      <div style={{
        position: 'absolute',
        top: 'var(--space-3)',
        right: 'var(--space-3)',
        zIndex: 10,
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-2)'
      }}>
        <button
          onClick={() => setZoom((z) => Math.min(2.5, z + 0.25))}
          className="btn btn-secondary btn-icon"
          title="Zoom In"
          aria-label="Zoom In"
        >
          <ZoomIn size={16} />
        </button>
        <button
          onClick={() => setZoom((z) => Math.max(0.75, z - 0.25))}
          className="btn btn-secondary btn-icon"
          title="Zoom Out"
          aria-label="Zoom Out"
        >
          <ZoomOut size={16} />
        </button>
        <button
          onClick={() => setZoom(1)}
          className="btn btn-secondary btn-icon"
          title="Reset View"
          aria-label="Reset View"
        >
          <RotateCcw size={16} />
        </button>
        <button
          onClick={() => setColorMode((m) => (m === 'elevation' ? 'state' : 'elevation'))}
          className="btn btn-secondary btn-icon"
          title="Toggle Elevation Coloring"
          aria-label="Toggle Elevation Coloring"
        >
          <Layers size={16} />
        </button>
      </div>

      {/* SVG Canvas Map */}
      <div style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'radial-gradient(circle at center, var(--bg-surface-elevated) 0%, var(--bg-app) 100%)',
        overflow: 'hidden'
      }}>
        <svg
          viewBox={`0 0 ${mapWidth} ${mapHeight}`}
          style={{
            width: '100%',
            height: '100%',
            transform: `scale(${zoom})`,
            transition: 'transform 200ms ease-out',
            cursor: 'grab'
          }}
        >
          {/* Subtle India outline indicator rings */}
          <circle cx="340" cy="380" r="260" fill="none" stroke="var(--chart-grid)" strokeWidth="1" strokeDasharray="6 6" />
          <circle cx="340" cy="380" r="160" fill="none" stroke="var(--chart-grid)" strokeWidth="1" strokeDasharray="4 4" />

          {/* Render Station Points */}
          {filteredStations.map((station) => {
            const { x, y } = project(station.latitude, station.longitude);
            const isSelected = filters.stationId === station.station_id;
            const isHovered = hoveredStation?.station_id === station.station_id;
            const color = getStationColor(station);

            return (
              <g
                key={station.station_id}
                onClick={() => handleStationClick(station)}
                onMouseEnter={() => setHoveredStation(station)}
                onMouseLeave={() => setHoveredStation(null)}
                style={{ cursor: 'pointer' }}
              >
                {/* Ping ring for selected station */}
                {isSelected && (
                  <circle cx={x} cy={y} r="12" fill="none" stroke="var(--accent-warning)" strokeWidth="2" opacity="0.7">
                    <animate attributeName="r" values="8;16;8" dur="2s" repeatCount="indefinite" />
                    <animate attributeName="opacity" values="0.8;0.2;0.8" dur="2s" repeatCount="indefinite" />
                  </circle>
                )}

                {/* Station circle point */}
                <circle
                  cx={x}
                  cy={y}
                  r={isSelected ? 6 : isHovered ? 5.5 : 3.5}
                  fill={color}
                  stroke="var(--bg-app)"
                  strokeWidth={isSelected || isHovered ? 2 : 1}
                  opacity={0.9}
                />
              </g>
            );
          })}
        </svg>
      </div>

      {/* Hover Information Tooltip */}
      {hoveredStation && (
        <div style={{
          position: 'absolute',
          bottom: 'var(--space-4)',
          left: 'var(--space-4)',
          background: 'var(--chart-tooltip-bg)',
          border: '1px solid var(--border-base)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-3) var(--space-4)',
          boxShadow: 'var(--shadow-lg)',
          zIndex: 20,
          pointerEvents: 'none',
          minWidth: '220px'
        }}>
          <div style={{ fontSize: 'var(--font-sm)', fontWeight: 700, color: 'var(--text-primary)' }}>
            {hoveredStation.station_name}
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--accent-primary)', marginTop: '2px' }}>
            {hoveredStation.district}, {hoveredStation.state}
          </div>
          <div style={{ display: 'flex', gap: 'var(--space-3)', marginTop: 'var(--space-2)', fontSize: 'var(--font-xs)', color: 'var(--text-secondary)' }}>
            <span>Elev: <b>{hoveredStation.elevation_m}m</b></span>
            <span>Lat: {hoveredStation.latitude.toFixed(2)}°</span>
            <span>Lon: {hoveredStation.longitude.toFixed(2)}°</span>
          </div>
          <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-tertiary)', marginTop: 'var(--space-1)' }}>
            Modern records: {hoveredStation.record_count_modern_2021_2025.toLocaleString()} days
          </div>
        </div>
      )}

      {/* Map Legend */}
      <div style={{
        position: 'absolute',
        bottom: 'var(--space-3)',
        right: 'var(--space-3)',
        zIndex: 10,
        background: 'var(--bg-surface-glass)',
        backdropFilter: 'blur(8px)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        padding: 'var(--space-2) var(--space-3)',
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
        fontSize: 'var(--font-2xs)',
        color: 'var(--text-secondary)'
      }}>
        <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Elevation Legend</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#c084fc' }} />
          <span>&gt; 1500m (Himalayan)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#38bdf8' }} />
          <span>600 - 1500m (Plateau)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#34d399' }} />
          <span>&lt; 600m (Plains/Coastal)</span>
        </div>
      </div>
    </div>
  );
};
