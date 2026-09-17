import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Download } from 'lucide-react';
import { GlobalFilterBar } from '../components/filters/GlobalFilterBar';
import { PreviewBanner } from '../components/common/PreviewBanner';
import { DataExplorerTable } from '../components/tables/DataExplorerTable';
import { weatherService, stationService } from '../services';
import { useFilters } from '../context/FilterContext';
import type { WeatherObservation } from '../types';

export const DataPage: React.FC = () => {
  const { filters, setScope } = useFilters();
  const [observations, setObservations] = useState<WeatherObservation[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    weatherService.getObservations(filters).then(setObservations);
  }, [filters]);

  const handleSelectStation = (stationId: string) => {
    stationService.getStationById(stationId).then((station) => {
      if (station) {
        setScope(station.state, station.district, station.station_id);
        navigate('/stations');
      }
    });
  };

  const handleExportCSV = () => {
    if (observations.length === 0) return;
    const headers = ['date_of_record', 'station_id', 'station_name', 'state', 'district', 'avg_temp', 'min_temp', 'max_temp', 'rainfall', 'wind_speed', 'air_pressure'];
    const rows = observations.map((o) => [
      o.date_of_record,
      o.station_id,
      `"${o.station_name || ''}"`,
      o.state || '',
      o.district || '',
      o.avg_temp ?? '',
      o.min_temp ?? '',
      o.max_temp ?? '',
      o.rainfall ?? '',
      o.wind_speed ?? '',
      o.air_pressure ?? ''
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `india_weather_records_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <PreviewBanner
        message="Canonical Observation Data Explorer"
        subtext="Direct inspection of canonical daily records. Missing rainfall records are preserved as nulls to eliminate artificial zero-inflation."
      />

      <GlobalFilterBar />

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontSize: 'var(--font-xl)', fontWeight: 800, color: 'var(--text-primary)' }}>
            Weather Observation Registry
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)' }}>
            Click station names to jump to detailed station telemetry
          </div>
        </div>

        <button
          onClick={handleExportCSV}
          className="btn btn-secondary btn-sm"
          style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
        >
          <Download size={14} />
          <span>Export Filtered CSV</span>
        </button>
      </div>

      <DataExplorerTable
        observations={observations}
        onSelectStation={handleSelectStation}
      />
    </div>
  );
};
