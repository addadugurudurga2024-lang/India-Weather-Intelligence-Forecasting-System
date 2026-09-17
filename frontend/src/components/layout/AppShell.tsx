import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { GlobalSearchModal } from './GlobalSearchModal';

export const AppShell: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-app)' }}>
      {/* Permanent on Desktop, Drawer on Mobile */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content Area */}
      <div 
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          minWidth: 0,
          transition: 'margin var(--transition-base)'
        }}
        className="main-content-layout"
      >
        <Header 
          onToggleSidebar={() => setSidebarOpen((prev) => !prev)} 
          onOpenSearch={() => setSearchOpen(true)}
        />
        
        <main style={{
          flex: 1,
          padding: 'var(--space-6)',
          maxWidth: '1600px',
          width: '100%',
          margin: '0 auto'
        }}>
          <Outlet />
        </main>
      </div>

      <GlobalSearchModal isOpen={searchOpen} onClose={() => setSearchOpen(false)} />

      <style>{`
        @media (min-width: 1024px) {
          .main-content-layout {
            margin-left: 260px;
          }
        }
      `}</style>
    </div>
  );
};
