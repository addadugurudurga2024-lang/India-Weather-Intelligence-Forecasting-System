import React, { useEffect, useState } from 'react';
import { Filter, RotateCcw } from 'lucide-react';
import { useFilters } from '../../context/FilterContext';
import { stationService } from '../../services';
import { stations } from '../../data';

export const GlobalFilterBar: React.FC = () => {
  const { filters, setFilter, resetFilters } = useFilters();
  const [states, setStates] = useState<string[]>([]);
  const [districts, setDistricts] = useState<string[]>([]);
  const [stationsList, setStationsList] = useState(stations);

  useEffect(() => {
    stationService.getStations().then(setStationsList);
    stationService.getStates().then(setStates);
  }, []);

  useEffect(() => {
    stationService.getDistrictsByState(filters.state).then((newDistricts) => {
      setDistricts(newDistricts);
      // Auto-sanitize: if current filters.district is not valid in new scope, reset to ALL
      if (filters.district !== 'ALL' && !newDistricts.includes(filters.district)) {
        setFilter('district', 'ALL');
      }
    });
  }, [filters.state, filters.district, setFilter]);

  const filteredStations = stationsList.filter((s) => {
    if (filters.state !== 'ALL' && s.state.toUpperCase() !== filters.state.toUpperCase()) return false;
    if (filters.district !== 'ALL' && s.district.toLowerCase() !== filters.district.toLowerCase()) return false;
    return true;
  });

  // Auto-sanitize station: if current filters.stationId is not in filteredStations, reset to ALL
  useEffect(() => {
    if (filters.stationId !== 'ALL') {
      const exists = filteredStations.some((s) => s.station_id === filters.stationId);
      if (!exists) {
        setFilter('stationId', 'ALL');
      }
    }
  }, [filteredStations, filters.stationId, setFilter]);

  return (
    <div className="card" style={{ marginBottom: 'var(--space-6)', padding: 'var(--space-4)' }}>
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 'var(--space-3)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Filter size={18} style={{ color: 'var(--accent-primary)' }} />
          <span style={{ fontWeight: 700, fontSize: 'var(--font-sm)', color: 'var(--text-primary)' }}>
            Filter Station Scope
          </span>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 'var(--space-3)', flex: 1, justifyContent: 'flex-end' }}>
          {/* State Dropdown */}
          <div style={{ minWidth: '140px' }}>
            <select
              className="select"
              value={filters.state}
              onChange={(e) => setFilter('state', e.target.value)}
              aria-label="Filter by State"
            >
              <option value="ALL">All States ({states.length})</option>
              {states.map((st) => (
                <option key={st} value={st}>{st}</option>
              ))}
            </select>
          </div>

          {/* District Dropdown */}
          <div style={{ minWidth: '160px' }}>
            <select
              className="select"
              value={filters.district}
              onChange={(e) => setFilter('district', e.target.value)}
              aria-label="Filter by District"
            >
              <option value="ALL">All Districts ({districts.length})</option>
              {districts.map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          {/* Station Dropdown */}
          <div style={{ minWidth: '200px' }}>
            <select
              className="select"
              value={filters.stationId}
              onChange={(e) => setFilter('stationId', e.target.value)}
              aria-label="Filter by Station"
            >
              <option value="ALL">All Stations ({filteredStations.length})</option>
              {filteredStations.map((s) => (
                <option key={s.station_id} value={s.station_id}>
                  {s.station_name} ({s.state})
                </option>
              ))}
            </select>
          </div>

          {/* Rainfall filter */}
          <div style={{ minWidth: '140px' }}>
            <select
              className="select"
              value={filters.rainfallFilter}
              onChange={(e) => setFilter('rainfallFilter', e.target.value as any)}
              aria-label="Filter by Rainfall Regime"
            >
              <option value="ALL">All Regimes</option>
              <option value="RAINY_ONLY">Rain Days (&gt; 0mm)</option>
              <option value="DRY_ONLY">Dry Days (0.0mm)</option>
            </select>
          </div>

          {/* Reset Button */}
          <button
            onClick={resetFilters}
            className="btn btn-secondary btn-sm"
            title="Reset all filters to pan-India defaults"
          >
            <RotateCcw size={14} />
            <span>Reset</span>
          </button>
        </div>
      </div>
    </div>
  );
};
