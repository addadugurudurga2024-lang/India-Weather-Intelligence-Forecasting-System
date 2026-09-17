import React from 'react';
import { Menu, Search, Sun, Moon, ShieldCheck, Database } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { useFilters } from '../../context/FilterContext';

interface HeaderProps {
  onToggleSidebar: () => void;
  onOpenSearch: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleSidebar, onOpenSearch }) => {
  const { resolvedTheme, toggleTheme } = useTheme();
  const { filters } = useFilters();

  return (
    <header style={{
      height: '64px',
      position: 'sticky',
      top: 0,
      zIndex: 'var(--z-header)',
      background: 'var(--bg-surface-glass)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border-subtle)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 var(--space-6)',
      gap: 'var(--space-4)'
    }}>
      {/* Left: Mobile Toggle & Context Breadcrumb */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
        <button
          onClick={onToggleSidebar}
          className="btn btn-ghost btn-icon mobile-menu-btn"
          aria-label="Toggle navigation menu"
          style={{ display: 'none' }}
        >
          <Menu size={20} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-2)',
            fontSize: 'var(--font-sm)',
            color: 'var(--text-secondary)'
          }}>
            <Database size={15} style={{ color: 'var(--accent-primary)' }} />
            <span>Scope:</span>
            <span style={{
              color: 'var(--text-primary)',
              fontWeight: 600,
              background: 'var(--bg-surface-elevated)',
              padding: '2px 8px',
              borderRadius: 'var(--radius-xs)',
              border: '1px solid var(--border-subtle)'
            }}>
              {filters.state === 'ALL' ? 'Pan-India (413 Stations)' : `State: ${filters.state}`}
            </span>
          </div>
        </div>
      </div>

      {/* Middle: Global Search Trigger */}
      <div style={{ flex: 1, maxWidth: '480px' }}>
        <button
          onClick={onOpenSearch}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: 'var(--space-2) var(--space-4)',
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-base)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--text-secondary)',
            fontSize: 'var(--font-sm)',
            cursor: 'pointer',
            transition: 'border-color var(--transition-fast)'
          }}
          onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'var(--accent-primary)')}
          onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-base)')}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <Search size={16} />
            <span>Search 413 stations, states, districts...</span>
          </div>
          <kbd style={{
            background: 'var(--bg-surface-elevated)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-xs)',
            padding: '1px 6px',
            fontSize: 'var(--font-2xs)',
            color: 'var(--text-tertiary)'
          }}>
            ⌘K
          </kbd>
        </button>
      </div>

      {/* Right: Immutability Tag & Theme Toggle */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
        <div 
          className="badge badge-primary desktop-badge"
          style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)', padding: '0.3rem 0.6rem' }}
          title="Authoritative Source SHA256: e6a63677... Verified"
        >
          <ShieldCheck size={14} />
          <span>SHA-256 AUDITED</span>
        </div>

        <button
          onClick={toggleTheme}
          className="btn btn-secondary btn-icon"
          aria-label={`Switch to ${resolvedTheme === 'dark' ? 'light' : 'dark'} mode`}
          title={`Switch to ${resolvedTheme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {resolvedTheme === 'dark' ? (
            <Sun size={18} style={{ color: 'var(--accent-warning)' }} />
          ) : (
            <Moon size={18} style={{ color: 'var(--accent-primary)' }} />
          )}
        </button>
      </div>

      <style>{`
        @media (max-width: 1023px) {
          .mobile-menu-btn {
            display: flex !important;
          }
          .desktop-badge {
            display: none !important;
          }
        }
      `}</style>
    </header>
  );
};
