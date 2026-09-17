import React from 'react';

export const LoadingState: React.FC<{ rows?: number }> = ({ rows = 4 }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', width: '100%', padding: 'var(--space-4)' }}>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton" style={{ height: '48px', width: '100%' }} />
      ))}
    </div>
  );
};

export const EmptyState: React.FC<{ title: string; message: string }> = ({ title, message }) => {
  return (
    <div className="card" style={{ padding: 'var(--space-8)', textAlign: 'center' }}>
      <div style={{ fontWeight: 700, fontSize: 'var(--font-lg)', color: 'var(--text-primary)', marginBottom: 'var(--space-2)' }}>
        {title}
      </div>
      <div style={{ fontSize: 'var(--font-sm)', color: 'var(--text-secondary)', maxWidth: '400px', margin: '0 auto' }}>
        {message}
      </div>
    </div>
  );
};
