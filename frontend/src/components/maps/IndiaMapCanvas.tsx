import React, { useState, useMemo, useRef, useCallback } from 'react';
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  ArrowRightLeft,
  Filter,
  Eye,
  EyeOff
} from 'lucide-react';
import type { Station } from '../../types';
import type { MapLayerId } from '../../types/geospatial';
import { useFilters } from '../../context/FilterContext';
import { GeographicService } from '../../services/geographicService';
import boundaryData from '../../data/indiaBoundaryPaths.json';

import { LayerControl } from './LayerControl';
import { TimeControl } from './TimeControl';
import { MapLegend } from './MapLegend';
import { MapTooltip } from './MapTooltip';
import { StationMarkerLayer } from './StationMarkerLayer';
import { StateOverlayLayer } from './StateOverlayLayer';
import { GeographicComparisonModal } from './GeographicComparisonModal';

interface IndiaMapCanvasProps {
  stations: Station[];
  onSelectStation?: (station: Station) => void;
  height?: number;
}

export const IndiaMapCanvas: React.FC<IndiaMapCanvasProps> = ({
  stations,
  onSelectStation,
  height = 720
}) => {
  const { filters, setScope } = useFilters();

  // Map viewport state
  const [zoom, setZoom] = useState<number>(1);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // Layer and metric selection
  const [activeLayer, setActiveLayer] = useState<MapLayerId>('stations');
  const [activeMetric, setActiveMetric] = useState<string>('default');
  const [showBoundaries, setShowBoundaries] = useState<boolean>(true);

  // Time navigation state
  const availableDates = useMemo(() => GeographicService.getAvailableObservationDates(), []);
  const [selectedDate, setSelectedDate] = useState<string>(
    availableDates.length > 0 ? availableDates[availableDates.length - 1] : '2025-02-10'
  );
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [speedMs, setSpeedMs] = useState<number>(1200);

  // Hover & selection states
  const [hoveredStation, setHoveredStation] = useState<Station | null>(null);
  const [hoveredState, setHoveredState] = useState<string | null>(null);

  // Comparison modal state
  const [isCompareOpen, setIsCompareOpen] = useState<boolean>(false);

  const containerRef = useRef<HTMLDivElement>(null);

  const mapWidth = 800;
  const mapHeight = 720;

  // Filter stations by global filter context
  const filteredStations = useMemo(() => {
    return stations.filter((s) => {
      if (filters.state !== 'ALL' && s.state !== filters.state) return false;
      if (filters.district !== 'ALL' && s.district !== filters.district) return false;
      return true;
    });
  }, [stations, filters]);

  // Observations and forecasts for selected date
  const currentObservations = useMemo(() => {
    return GeographicService.getObservationsForDate(selectedDate);
  }, [selectedDate]);

  const currentForecasts = useMemo(() => {
    return GeographicService.getForecastsForDate(selectedDate);
  }, [selectedDate]);

  const regions = useMemo(() => GeographicService.getAllRegions(), []);

  // Selection handler
  const handleStationClick = (station: Station) => {
    setScope(station.state, station.district, station.station_id);
    if (onSelectStation) onSelectStation(station);
  };

  const handleStateClick = (stateName: string) => {
    if (filters.state === stateName) {
      setScope('ALL', 'ALL', 'ALL');
    } else {
      setScope(stateName, 'ALL', 'ALL');
    }
  };

  // Zoom and Pan controls
  const handleZoomIn = () => setZoom((z) => Math.min(4.0, z + 0.35));
  const handleZoomOut = () => setZoom((z) => Math.max(0.75, z - 0.35));
  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  // Mouse drag handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return; // primary click only
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging) return;
    setPan({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    });
  }, [isDragging, dragStart]);

  const handleMouseUp = () => setIsDragging(false);

  // Wheel zoom
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.88;
    setZoom((z) => Math.min(4.0, Math.max(0.75, z * zoomFactor)));
  };

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === '+' || e.key === '=') handleZoomIn();
    if (e.key === '-' || e.key === '_') handleZoomOut();
    if (e.key === '0') handleReset();
    if (e.key === 'ArrowLeft') setPan((p) => ({ ...p, x: p.x + 30 }));
    if (e.key === 'ArrowRight') setPan((p) => ({ ...p, x: p.x - 30 }));
    if (e.key === 'ArrowUp') setPan((p) => ({ ...p, y: p.y + 30 }));
    if (e.key === 'ArrowDown') setPan((p) => ({ ...p, y: p.y - 30 }));
  };

  return (
    <div
      ref={containerRef}
      tabIndex={0}
      onKeyDown={handleKeyDown}
      style={{
        position: 'relative',
        width: '100%',
        height,
        borderRadius: 'var(--radius-xl)',
        overflow: 'hidden',
        border: '1px solid var(--border-base)',
        background: 'radial-gradient(ellipse at 50% 40%, var(--bg-surface-elevated) 0%, var(--bg-app) 100%)',
        outline: 'none',
        userSelect: 'none'
      }}
      aria-label="Interactive India Weather Telemetry & Forecast Map"
    >
      {/* Top Left: Layer Selector HUD */}
      <div style={{
        position: 'absolute',
        top: 'var(--space-3)',
        left: 'var(--space-3)',
        zIndex: 20,
        maxWidth: 'calc(100% - 100px)'
      }}>
        <LayerControl
          activeLayer={activeLayer}
          onLayerChange={setActiveLayer}
          activeMetric={activeMetric}
          onMetricChange={setActiveMetric}
        />
      </div>

      {/* Top Right: Zoom & View Controls */}
      <div style={{
        position: 'absolute',
        top: 'var(--space-3)',
        right: 'var(--space-3)',
        zIndex: 20,
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-2)'
      }}>
        <button
          onClick={handleZoomIn}
          className="btn btn-secondary btn-icon"
          title="Zoom In (+)"
          aria-label="Zoom In"
        >
          <ZoomIn size={16} />
        </button>
        <button
          onClick={handleZoomOut}
          className="btn btn-secondary btn-icon"
          title="Zoom Out (-)"
          aria-label="Zoom Out"
        >
          <ZoomOut size={16} />
        </button>
        <button
          onClick={handleReset}
          className="btn btn-secondary btn-icon"
          title="Reset View (0)"
          aria-label="Reset View"
        >
          <RotateCcw size={16} />
        </button>
        <button
          onClick={() => setShowBoundaries((b) => !b)}
          className={`btn ${showBoundaries ? 'btn-secondary' : 'btn-ghost'} btn-icon`}
          title={showBoundaries ? 'Hide Boundaries' : 'Show Boundaries'}
          aria-label="Toggle Geographic Boundaries"
        >
          {showBoundaries ? <Eye size={16} /> : <EyeOff size={16} />}
        </button>
        <button
          onClick={() => setIsCompareOpen(true)}
          className="btn btn-primary btn-icon"
          title="Compare Locations"
          aria-label="Compare Locations"
        >
          <ArrowRightLeft size={16} />
        </button>
      </div>

      {/* Active Filter & Station Status Pill */}
      <div style={{
        position: 'absolute',
        top: '128px',
        left: 'var(--space-3)',
        zIndex: 15,
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-2)',
        background: 'var(--bg-surface-glass)',
        backdropFilter: 'blur(8px)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        padding: '4px 10px',
        fontSize: 'var(--font-xs)',
        color: 'var(--text-secondary)'
      }}>
        <Filter size={13} style={{ color: 'var(--accent-primary)' }} />
        <span><b>{filteredStations.length}</b> of 413 Stations Active</span>
        {filters.state !== 'ALL' && (
          <span className="badge badge-primary" style={{ fontSize: '10px' }}>
            {filters.state}
          </span>
        )}
        {filters.district !== 'ALL' && (
          <span className="badge badge-neutral" style={{ fontSize: '10px' }}>
            {filters.district}
          </span>
        )}
      </div>

      {/* Primary SVG Rendering Canvas */}
      <div
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: isDragging ? 'grabbing' : 'grab'
        }}
      >
        <svg
          viewBox={`0 0 ${mapWidth} ${mapHeight}`}
          style={{
            width: '100%',
            height: '100%',
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: 'center center',
            transition: isDragging ? 'none' : 'transform 180ms ease-out'
          }}
        >
          <defs>
            {/* Subtle radial glow filter for dark theme */}
            <radialGradient id="indiaGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="var(--accent-primary)" stopOpacity="0.08" />
              <stop offset="100%" stopColor="transparent" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Background Ambient Glow */}
          <rect x="100" y="40" width="600" height="640" fill="url(#indiaGlow)" pointerEvents="none" />

          {/* India National Cartographic Boundary */}
          {showBoundaries && (
            <g id="national-boundary-group" pointerEvents="none">
              <path
                d={(boundaryData as any).national_boundary}
                fill="none"
                stroke="var(--border-base)"
                strokeWidth="1.6"
                strokeLinejoin="round"
                opacity={0.7}
              />
              <path
                d={(boundaryData as any).national_boundary}
                fill="var(--bg-surface)"
                opacity={0.25}
              />
            </g>
          )}

          {/* State Regional Layer */}
          <StateOverlayLayer
            regions={regions}
            selectedState={filters.state !== 'ALL' ? filters.state : null}
            hoveredState={hoveredState}
            onSelectState={handleStateClick}
            onHoverState={setHoveredState}
            activeLayer={activeLayer}
          />

          {/* 413 Station Markers */}
          <StationMarkerLayer
            stations={filteredStations}
            activeLayer={activeLayer}
            activeMetric={activeMetric}
            selectedStationId={filters.stationId !== 'ALL' ? filters.stationId : null}
            hoveredStationId={hoveredStation?.station_id ?? null}
            observations={currentObservations}
            forecasts={currentForecasts}
            onSelectStation={handleStationClick}
            onHoverStation={setHoveredStation}
            zoom={zoom}
          />
        </svg>
      </div>

      {/* Floating Hover Tooltip */}
      {hoveredStation && (
        <div style={{
          position: 'absolute',
          bottom: '80px',
          left: 'var(--space-4)',
          zIndex: 30
        }}>
          <MapTooltip
            station={hoveredStation}
            activeLayer={activeLayer}
            selectedDate={selectedDate}
            isForecast={activeLayer === 'forecast_overlay'}
          />
        </div>
      )}

      {/* Bottom Right: Map Legend */}
      <div style={{
        position: 'absolute',
        bottom: 'var(--space-4)',
        right: 'var(--space-4)',
        zIndex: 20
      }}>
        <MapLegend activeLayer={activeLayer} activeMetric={activeMetric} />
      </div>

      {/* Bottom Center: Timeline / Playback Controls */}
      <div style={{
        position: 'absolute',
        bottom: 'var(--space-4)',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 20,
        width: 'calc(100% - 320px)',
        maxWidth: '560px'
      }}>
        <TimeControl
          dates={availableDates}
          selectedDate={selectedDate}
          onDateChange={setSelectedDate}
          isPlaying={isPlaying}
          onTogglePlay={() => setIsPlaying((p) => !p)}
          speedMs={speedMs}
          onSpeedChange={setSpeedMs}
          isForecast={activeLayer === 'forecast_overlay'}
        />
      </div>

      {/* Multi-Location Comparison Modal */}
      <GeographicComparisonModal
        isOpen={isCompareOpen}
        onClose={() => setIsCompareOpen(false)}
        stations={stations}
        initialStationIds={filters.stationId !== 'ALL' ? [filters.stationId] : []}
        selectedDate={selectedDate}
      />
    </div>
  );
};
