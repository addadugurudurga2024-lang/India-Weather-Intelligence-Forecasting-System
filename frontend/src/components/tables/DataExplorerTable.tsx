import React, { useState, useMemo } from 'react';
import { ArrowUpDown, ChevronLeft, ChevronRight, Eye, AlertCircle } from 'lucide-react';
import type { WeatherObservation } from '../../types';

interface DataExplorerTableProps {
  observations: WeatherObservation[];
  onSelectStation?: (stationId: string) => void;
}

export const DataExplorerTable: React.FC<DataExplorerTableProps> = ({
  observations,
  onSelectStation
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [sortField, setSortField] = useState<keyof WeatherObservation>('date_of_record');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [filterQuery, setFilterQuery] = useState('');
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  // Sorting and filtering
  const processedData = useMemo(() => {
    let result = [...observations];

    if (filterQuery.trim()) {
      const q = filterQuery.toLowerCase();
      result = result.filter((row) =>
        row.station_name?.toLowerCase().includes(q) ||
        row.state?.toLowerCase().includes(q) ||
        row.district?.toLowerCase().includes(q) ||
        row.date_of_record.includes(q)
      );
    }

    result.sort((a, b) => {
      const valA = a[sortField];
      const valB = b[sortField];
      if (valA === null || valA === undefined) return 1;
      if (valB === null || valB === undefined) return -1;
      if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
      if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [observations, filterQuery, sortField, sortOrder]);

  const totalPages = Math.ceil(processedData.length / pageSize) || 1;
  const startIndex = (currentPage - 1) * pageSize;
  const currentRows = processedData.slice(startIndex, startIndex + pageSize);

  const handleSort = (field: keyof WeatherObservation) => {
    if (sortField === field) {
      setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', padding: 0 }}>
      {/* Table Controls */}
      <div style={{
        padding: 'var(--space-4) var(--space-5)',
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 'var(--space-3)',
        borderBottom: '1px solid var(--border-subtle)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <input
            type="text"
            className="input"
            placeholder="Search rows by station, date..."
            value={filterQuery}
            onChange={(e) => {
              setFilterQuery(e.target.value);
              setCurrentPage(1);
            }}
            style={{ width: '260px' }}
          />
          <span style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)' }}>
            Showing <b>{processedData.length.toLocaleString()}</b> records
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <label style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)' }}>Rows per page:</label>
          <select
            className="select"
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value));
              setCurrentPage(1);
            }}
            style={{ width: '80px', padding: '0.35rem' }}
          >
            <option value={10}>10</option>
            <option value={15}>15</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
          </select>
        </div>
      </div>

      {/* Table Viewport */}
      <div className="data-table-container" style={{ border: 'none', borderRadius: 0 }}>
        <table className="data-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('date_of_record')} style={{ cursor: 'pointer' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                  <span>Date</span>
                  <ArrowUpDown size={13} />
                </div>
              </th>
              <th onClick={() => handleSort('station_name')} style={{ cursor: 'pointer' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                  <span>Station</span>
                  <ArrowUpDown size={13} />
                </div>
              </th>
              <th>Location</th>
              <th onClick={() => handleSort('avg_temp')} style={{ cursor: 'pointer' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                  <span>Avg Temp</span>
                  <ArrowUpDown size={13} />
                </div>
              </th>
              <th>Min / Max</th>
              <th onClick={() => handleSort('rainfall')} style={{ cursor: 'pointer' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                  <span>Rainfall (mm)</span>
                  <ArrowUpDown size={13} />
                </div>
              </th>
              <th>Wind (km/h)</th>
              <th>Pressure (hPa)</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {currentRows.length === 0 ? (
              <tr>
                <td colSpan={9} style={{ textAlign: 'center', padding: 'var(--space-8)', color: 'var(--text-tertiary)' }}>
                  No matching weather observations found.
                </td>
              </tr>
            ) : (
              currentRows.map((row) => {
                const rowKey = `${row.station_id}-${row.date_of_record}`;
                const isExpanded = expandedRow === rowKey;
                const isMissingRain = row.rainfall === null;

                return (
                  <React.Fragment key={rowKey}>
                    <tr>
                      <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                        {row.date_of_record}
                      </td>
                      <td>
                        <button
                          onClick={() => onSelectStation && onSelectStation(row.station_id)}
                          style={{
                            background: 'none',
                            border: 'none',
                            color: 'var(--accent-primary)',
                            fontWeight: 600,
                            cursor: 'pointer',
                            textAlign: 'left',
                            padding: 0
                          }}
                        >
                          {row.station_name || row.station_id}
                        </button>
                      </td>
                      <td style={{ color: 'var(--text-secondary)' }}>
                        {row.district}, {row.state}
                      </td>
                      <td style={{ fontWeight: 700, color: 'var(--accent-temp)' }}>
                        {row.avg_temp !== null ? `${row.avg_temp}°C` : 'NaN'}
                      </td>
                      <td style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)' }}>
                        {row.min_temp ?? '-'}° / {row.max_temp ?? '-'}°
                      </td>
                      <td>
                        {isMissingRain ? (
                          <span className="badge badge-warning" title="Rainfall gauge observation unavailable (not imputed as zero)">
                            <AlertCircle size={11} />
                            <span>MISSING</span>
                          </span>
                        ) : row.rainfall! > 0 ? (
                          <span className="badge badge-rain" style={{ fontWeight: 700 }}>
                            {row.rainfall} mm
                          </span>
                        ) : (
                          <span style={{ color: 'var(--text-tertiary)' }}>0.0 mm</span>
                        )}
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{row.wind_speed ?? '-'}</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{row.air_pressure ?? '-'}</td>
                      <td>
                        <button
                          onClick={() => setExpandedRow(isExpanded ? null : rowKey)}
                          className="btn btn-ghost btn-sm"
                          style={{ padding: '0.2rem 0.5rem' }}
                          aria-label="Toggle details"
                        >
                          <Eye size={14} />
                        </button>
                      </td>
                    </tr>

                    {/* Row Expansion Details */}
                    {isExpanded && (
                      <tr style={{ background: 'var(--bg-surface-elevated)' }}>
                        <td colSpan={9} style={{ padding: 'var(--space-4) var(--space-6)' }}>
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)', fontSize: 'var(--font-xs)' }}>
                            <div>
                              <div style={{ color: 'var(--text-tertiary)' }}>Station Composite ID</div>
                              <div style={{ fontWeight: 600, color: 'var(--text-primary)', wordBreak: 'break-all' }}>{row.station_id}</div>
                            </div>
                            <div>
                              <div style={{ color: 'var(--text-tertiary)' }}>Precipitation Quality</div>
                              <div style={{ color: isMissingRain ? 'var(--accent-warning)' : 'var(--accent-success)', fontWeight: 600 }}>
                                {isMissingRain ? 'Unavailable Gauge reading (Preserved Null)' : row.rainfall! > 0 ? 'Active Rain (>0mm)' : 'Dry Day (Verified 0.0mm)'}
                              </div>
                            </div>
                            <div>
                              <div style={{ color: 'var(--text-tertiary)' }}>Atmospheric Diurnal Range</div>
                              <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                                {row.max_temp !== null && row.min_temp !== null ? `${(row.max_temp - row.min_temp).toFixed(1)}°C` : 'N/A'}
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div style={{
        padding: 'var(--space-3) var(--space-5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderTop: '1px solid var(--border-subtle)',
        fontSize: 'var(--font-xs)',
        color: 'var(--text-secondary)'
      }}>
        <span>
          Showing page <b>{currentPage}</b> of <b>{totalPages}</b>
        </span>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="btn btn-secondary btn-sm"
            aria-label="Previous Page"
          >
            <ChevronLeft size={14} />
            <span>Prev</span>
          </button>
          <button
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="btn btn-secondary btn-sm"
            aria-label="Next Page"
          >
            <span>Next</span>
            <ChevronRight size={14} />
          </button>
        </div>
      </div>
    </div>
  );
};
