import React, { useState, useEffect } from 'react';
import { Search, X, MapPin, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { stations } from '../../data';
import { useFilters } from '../../context/FilterContext';

interface GlobalSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const GlobalSearchModal: React.FC<GlobalSearchModalProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();
  const { setScope } = useFilters();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) {
          onClose();
        }
      } else if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const cleanQuery = query.toLowerCase().trim();
  const matchedStations = cleanQuery
    ? stations
        .filter(
          (s) =>
            s.station_name.toLowerCase().includes(cleanQuery) ||
            s.district.toLowerCase().includes(cleanQuery) ||
            s.state.toLowerCase().includes(cleanQuery) ||
            s.station_id.toLowerCase().includes(cleanQuery)
        )
        .slice(0, 8)
    : [];

  const handleSelectStation = (stationId: string, state: string, district: string) => {
    setScope(state, district, stationId);
    onClose();
    navigate('/stations');
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(6px)',
        zIndex: 'var(--z-modal)',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '12vh'
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{
          width: '100%',
          maxWidth: '640px',
          background: 'var(--bg-surface)',
          padding: 0,
          overflow: 'hidden',
          boxShadow: 'var(--shadow-lg)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-3)',
          padding: 'var(--space-4) var(--space-5)',
          borderBottom: '1px solid var(--border-base)'
        }}>
          <Search size={20} style={{ color: 'var(--accent-primary)' }} />
          <input
            type="text"
            placeholder="Search stations, districts, states, or IDs..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              color: 'var(--text-primary)',
              fontSize: 'var(--font-base)',
              outline: 'none'
            }}
          />
          <button onClick={onClose} className="btn btn-ghost btn-icon" aria-label="Close search">
            <X size={18} />
          </button>
        </div>

        {/* Results List */}
        <div style={{ maxHeight: '380px', overflowY: 'auto', padding: 'var(--space-2)' }}>
          {query.trim() === '' ? (
            <div style={{ padding: 'var(--space-6)', textAlign: 'center', color: 'var(--text-tertiary)', fontSize: 'var(--font-sm)' }}>
              Type a station name like "Delhi", "Bengaluru", "Shimla", or state code "MH"...
            </div>
          ) : matchedStations.length === 0 ? (
            <div style={{ padding: 'var(--space-6)', textAlign: 'center', color: 'var(--text-tertiary)', fontSize: 'var(--font-sm)' }}>
              No canonical station found matching "{query}".
            </div>
          ) : (
            matchedStations.map((s) => (
              <div
                key={s.station_id}
                onClick={() => handleSelectStation(s.station_id, s.state, s.district)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: 'var(--space-3) var(--space-4)',
                  borderRadius: 'var(--radius-md)',
                  cursor: 'pointer',
                  transition: 'background var(--transition-fast)'
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-surface-hover)')}
                onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                  <div style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--accent-primary-subtle)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--accent-primary)'
                  }}>
                    <MapPin size={16} />
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 'var(--font-sm)', color: 'var(--text-primary)' }}>
                      {s.station_name}
                    </div>
                    <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)' }}>
                      {s.district}, {s.state} • Elev: {s.elevation_m}m
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  <span className="badge badge-neutral">{s.state}</span>
                  <ExternalLink size={14} style={{ color: 'var(--text-tertiary)' }} />
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
