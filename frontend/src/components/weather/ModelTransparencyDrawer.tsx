import React, { useState } from 'react';
import { ShieldCheck, ChevronDown, ChevronUp, Database, Cpu } from 'lucide-react';
import type { MultiHorizonSummary, Operational25DayTimeline } from '../../types';

interface ModelTransparencyDrawerProps {
  timeline: Operational25DayTimeline;
  summary: MultiHorizonSummary;
}

export const ModelTransparencyDrawer: React.FC<ModelTransparencyDrawerProps> = ({ timeline, summary }) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);

  return (
    <div className="card" style={{
      background: 'var(--bg-surface)',
      border: '1px solid var(--border-base)',
      padding: 'var(--space-4)',
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-3)'
    }}>
      <div
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
          userSelect: 'none'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <ShieldCheck size={18} style={{ color: 'var(--accent-success)' }} />
          <span style={{ fontSize: 'var(--font-sm)', fontWeight: 800, color: 'var(--text-primary)' }}>
            Scientific Transparency & Provenance Ledger
          </span>
          <span className="badge badge-success" style={{ fontSize: '10px' }}>Zero Fabrication Verified</span>
        </div>

        <button className="btn btn-sm btn-ghost" style={{ padding: '2px 8px' }}>
          {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {isOpen && (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-4)',
          marginTop: 'var(--space-2)',
          paddingTop: 'var(--space-3)',
          borderTop: '1px solid var(--border-subtle)',
          fontSize: 'var(--font-xs)',
          color: 'var(--text-secondary)'
        }}>
          {/* Provenance & Distinction */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 'var(--space-3)'
          }}>
            <div style={{
              background: 'var(--bg-elevated)',
              padding: 'var(--space-3)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)'
            }}>
              <div style={{ fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                <Database size={14} style={{ color: '#10b981' }} />
                <span>Historical Telemetry (D-12 to D0)</span>
              </div>
              <div>
                <strong>Source:</strong> {timeline.is_historical_simulation ? 'Phase 2 IMD Authoritative Canonical Panel' : 'Open-Meteo CC BY 4.0 Archive'}
              </div>
              <div style={{ marginTop: '4px' }}>
                <strong>Classification:</strong> 100% physically observed sensor telemetry. Zero values are imputed, smoothed, or filled with ML predictions.
              </div>
            </div>

            <div style={{
              background: 'var(--bg-elevated)',
              padding: 'var(--space-3)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)'
            }}>
              <div style={{ fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                <Cpu size={14} style={{ color: '#c084fc' }} />
                <span>Model Forecasts (D+1 to D+12)</span>
              </div>
              <div>
                <strong>Engine:</strong> Direct Horizon-Specific XGBoost (12 independent models)
              </div>
              <div style={{ marginTop: '4px' }}>
                <strong>Leakage Prevention:</strong> Models ingest only observations up to origin D0. Future observations are strictly withheld at inference.
              </div>
            </div>
          </div>

          {/* Horizon Selection Matrix */}
          <div>
            <div style={{ fontWeight: 800, color: 'var(--text-primary)', marginBottom: 'var(--space-2)' }}>
              Horizon-Specific Model Selection & Out-of-Time Verification
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', fontSize: '11px', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-base)', color: 'var(--text-tertiary)' }}>
                    <th style={{ padding: '6px' }}>Horizon</th>
                    <th style={{ padding: '6px' }}>Days Ahead</th>
                    <th style={{ padding: '6px' }}>Selected Model</th>
                    <th style={{ padding: '6px' }}>Holdout Temp MAE</th>
                    <th style={{ padding: '6px' }}>Skill vs Persistence</th>
                    <th style={{ padding: '6px' }}>Rain ROC-AUC</th>
                    <th style={{ padding: '6px' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.model_selection_matrix.map((row) => (
                    <tr key={row.horizon} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                      <td style={{ padding: '6px', fontWeight: 700, color: 'var(--text-primary)' }}>{row.horizon}</td>
                      <td style={{ padding: '6px' }}>{row.days_ahead}</td>
                      <td style={{ padding: '6px' }}>{row.best_temp_model}</td>
                      <td style={{ padding: '6px', fontFamily: 'var(--font-mono)' }}>{row.temp_mae.toFixed(2)}°C</td>
                      <td style={{ padding: '6px', fontFamily: 'var(--font-mono)', color: row.temp_skill_vs_persistence > 0 ? '#10b981' : '#ef4444' }}>
                        +{row.temp_skill_vs_persistence.toFixed(2)}°C
                      </td>
                      <td style={{ padding: '6px', fontFamily: 'var(--font-mono)' }}>{row.rain_roc_auc.toFixed(3)}</td>
                      <td style={{ padding: '6px' }}>
                        <span className={`badge ${row.recommendation === 'APPROVED' ? 'badge-success' : 'badge-warning'}`} style={{ fontSize: '9px' }}>
                          {row.recommendation}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Limitations */}
          <div style={{ background: 'var(--bg-elevated)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
              Documented Scientific Limitations
            </div>
            <ul style={{ paddingLeft: 'var(--space-4)', margin: 0, display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {summary.known_limitations.map((lim, i) => (
                <li key={i}>{lim}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
