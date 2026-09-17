import React from 'react';
import type { GeographicRegion } from '../../types/geospatial';
import boundaryData from '../../data/indiaBoundaryPaths.json';

interface StateOverlayLayerProps {
  regions: GeographicRegion[];
  selectedState: string | null;
  hoveredState: string | null;
  onSelectState: (stateName: string) => void;
  onHoverState: (stateName: string | null) => void;
  activeLayer: string;
}

export const StateOverlayLayer: React.FC<StateOverlayLayerProps> = ({
  regions,
  selectedState,
  hoveredState,
  onSelectState,
  onHoverState,
  activeLayer
}) => {
  const statePolygons = (boundaryData as any).states || [];

  const getStateDensityColor = (count: number) => {
    if (count > 25) return 'rgba(56, 189, 248, 0.28)';
    if (count >= 10) return 'rgba(52, 211, 153, 0.22)';
    if (count >= 5) return 'rgba(250, 204, 21, 0.18)';
    return 'rgba(148, 163, 184, 0.12)';
  };

  return (
    <g id="state-overlay-layer">
      {statePolygons.map((stateItem: any) => {
        const isSelected = selectedState === stateItem.state_name;
        const isHovered = hoveredState === stateItem.state_name;
        const region = regions.find((r) => r.name === stateItem.state_name);
        const count = region?.station_count || stateItem.station_count;

        const fillColor = activeLayer === 'state_density'
          ? getStateDensityColor(count)
          : isSelected
          ? 'rgba(56, 189, 248, 0.20)'
          : isHovered
          ? 'rgba(255, 255, 255, 0.08)'
          : 'transparent';

        const strokeColor = isSelected
          ? 'var(--accent-primary)'
          : isHovered
          ? 'var(--text-secondary)'
          : 'var(--chart-grid)';

        return (
          <g
            key={stateItem.state_name}
            onClick={(e) => {
              e.stopPropagation();
              onSelectState(stateItem.state_name);
            }}
            onMouseEnter={() => onHoverState(stateItem.state_name)}
            onMouseLeave={() => onHoverState(null)}
            style={{ cursor: 'pointer' }}
          >
            <path
              d={stateItem.path_d}
              fill={fillColor}
              stroke={strokeColor}
              strokeWidth={isSelected ? 2 : isHovered ? 1.5 : 0.6}
              strokeDasharray={isSelected ? undefined : '3 3'}
              opacity={0.85}
              style={{ transition: 'all var(--transition-fast)' }}
            />
            {/* Centroid label for state density or selected state */}
            {(activeLayer === 'state_density' || isSelected) && (
              <text
                x={stateItem.centroid_x}
                y={stateItem.centroid_y}
                textAnchor="middle"
                fill="var(--text-primary)"
                fontSize="10px"
                fontWeight={700}
                pointerEvents="none"
                style={{
                  paintOrder: 'stroke',
                  stroke: 'var(--bg-app)',
                  strokeWidth: '2.5px',
                  strokeLinecap: 'round'
                }}
              >
                {stateItem.state_name} ({count})
              </text>
            )}
          </g>
        );
      })}
    </g>
  );
};
