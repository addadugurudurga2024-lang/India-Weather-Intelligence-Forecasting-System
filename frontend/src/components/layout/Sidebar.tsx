import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  LineChart,
  CloudSun,
  CloudRain,
  MapPin,
  Map,
  Cpu,
  Database,
  BookOpen,
  X,
  Compass,
  CalendarDays
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navItems = [
  { path: '/dashboard', label: 'Overview Dashboard', icon: LayoutDashboard },
  { path: '/analytics', label: 'Temperature Analytics', icon: LineChart },
  { path: '/rainfall', label: 'Rainfall Intelligence', icon: CloudRain },
  { path: '/forecast', label: 'Forecast Center', icon: CloudSun },
  { path: '/long-term-predictor', label: 'Long-Term Predictor', icon: CalendarDays },
  { path: '/stations', label: 'Station Explorer', icon: MapPin },
  { path: '/map', label: 'Geographic Map', icon: Map },
  { path: '/models', label: 'Model Performance', icon: Cpu },
  { path: '/data', label: 'Data Explorer', icon: Database },
  { path: '/methodology', label: 'Scientific Methodology', icon: BookOpen },
];

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div 
          onClick={onClose}
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.6)',
            backdropFilter: 'blur(4px)',
            zIndex: 'var(--z-sidebar)'
          }}
        />
      )}

      <aside
        style={{
          width: '260px',
          height: '100vh',
          position: 'fixed',
          top: 0,
          left: 0,
          background: 'var(--bg-surface)',
          borderRight: '1px solid var(--border-subtle)',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 'calc(var(--z-sidebar) + 1)',
          transform: isOpen ? 'translateX(0)' : 'translateX(-100%)',
          transition: 'transform var(--transition-base)',
        }}
        className="sidebar-container"
      >
        {/* Brand Header */}
        <div style={{
          padding: 'var(--space-5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--border-subtle)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-rain) 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#090d16',
              boxShadow: 'var(--shadow-glow-blue)'
            }}>
              <Compass size={22} strokeWidth={2.4} />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: 'var(--font-base)', letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
                INDIA WEATHER
              </div>
              <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--accent-primary)', fontWeight: 600, letterSpacing: '0.05em' }}>
                INTELLIGENCE SYSTEM
              </div>
            </div>
          </div>
          
          <button 
            onClick={onClose} 
            className="btn btn-ghost btn-icon mobile-only-close"
            style={{ display: 'none' }}
            aria-label="Close sidebar"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation Items */}
        <nav style={{ flex: 1, padding: 'var(--space-4)', overflowY: 'auto' }}>
          <div style={{
            fontSize: 'var(--font-2xs)',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: 'var(--text-tertiary)',
            padding: '0 var(--space-3) var(--space-2)'
          }}>
            Platform Navigation
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => {
                    if (window.innerWidth < 1024) onClose();
                  }}
                  style={({ isActive }) => ({
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-3)',
                    padding: 'var(--space-3) var(--space-4)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: 'var(--font-sm)',
                    fontWeight: isActive ? 600 : 500,
                    textDecoration: 'none',
                    color: isActive ? 'var(--accent-primary)' : 'var(--text-secondary)',
                    background: isActive ? 'var(--accent-primary-subtle)' : 'transparent',
                    borderLeft: isActive ? '3px solid var(--accent-primary)' : '3px solid transparent',
                    transition: 'all var(--transition-fast)'
                  })}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </div>
        </nav>

        {/* Phase Footer Status */}
        <div style={{
          padding: 'var(--space-4)',
          borderTop: '1px solid var(--border-subtle)',
          background: 'var(--bg-surface-elevated)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-2)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)' }}>System Stage</span>
            <span className="badge badge-success">Phase 9 Active</span>
          </div>
          <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-secondary)' }}>
            Canonical 413 Stations • XGBoost + LSTM Verified
          </div>
        </div>
      </aside>

      <style>{`
        @media (min-width: 1024px) {
          .sidebar-container {
            transform: translateX(0) !important;
          }
        }
        @media (max-width: 1023px) {
          .mobile-only-close {
            display: flex !important;
          }
        }
      `}</style>
    </>
  );
};
