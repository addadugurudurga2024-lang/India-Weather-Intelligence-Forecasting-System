import React from 'react';
import { BookOpen, ShieldCheck, GitBranch, Layers, AlertCircle, Database } from 'lucide-react';
import { PreviewBanner } from '../components/common/PreviewBanner';

export const MethodologyPage: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', maxWidth: '1000px', margin: '0 auto' }}>
      <PreviewBanner
        message="Platform Engineering &amp; Scientific Methodology"
        subtext="Complete mathematical specifications, data immutability guarantees, and machine learning validation protocols."
      />

      {/* Header */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-2)' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--accent-primary-subtle)',
            color: 'var(--accent-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <BookOpen size={20} />
          </div>
          <div>
            <div style={{ fontSize: 'var(--font-2xl)', fontWeight: 800, color: 'var(--text-primary)' }}>
              Scientific Methodology &amp; Architecture
            </div>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)' }}>
              India Weather Forecasting &amp; Intelligence System
            </div>
          </div>
        </div>
      </div>

      {/* Core Principles Section */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
        <div style={{ fontSize: 'var(--font-lg)', fontWeight: 700, color: 'var(--text-primary)' }}>
          1. Non-Negotiable Scientific Principles
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-4)' }}>
          <div style={{ padding: 'var(--space-4)', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--accent-success)', fontWeight: 700, fontSize: 'var(--font-sm)' }}>
              <ShieldCheck size={16} />
              <span>Raw Data Immutability</span>
            </div>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: 'var(--space-2)', lineHeight: 1.6 }}>
              The authoritative raw Excel source (<code style={{ fontFamily: 'var(--font-mono)' }}>india_weather_rainfall_data.xlsx</code>) is byte-for-byte immutable. Verified SHA-256 hash: <code style={{ fontFamily: 'var(--font-mono)' }}>e6a636777430f078b4d970f9f46e79efcece7f97b67dd186c30a755d2783cd84</code>.
            </div>
          </div>

          <div style={{ padding: 'var(--space-4)', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--accent-warning)', fontWeight: 700, fontSize: 'var(--font-sm)' }}>
              <AlertCircle size={16} />
              <span>Missing Rainfall != Zero Rainfall</span>
            </div>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: 'var(--space-2)', lineHeight: 1.6 }}>
              8,330 station records (1.38%) lacking valid next-day rainfall are preserved as missing (null) rather than zero-imputed, preventing artificial dry bias in supervised modeling.
            </div>
          </div>

          <div style={{ padding: 'var(--space-4)', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--accent-primary)', fontWeight: 700, fontSize: 'var(--font-sm)' }}>
              <GitBranch size={16} />
              <span>Walk-Forward Expanding Cross-Validation</span>
            </div>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: 'var(--space-2)', lineHeight: 1.6 }}>
              Random train/test splits are strictly prohibited. Fold 1 (Train 2021-22 / Val 2023) and Fold 2 (Train 2021-23 / Val 2024) respect time-series causality, with a sealed 2025 out-of-time holdout.
            </div>
          </div>

          <div style={{ padding: 'var(--space-4)', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--accent-purple)', fontWeight: 700, fontSize: 'var(--font-sm)' }}>
              <Layers size={16} />
              <span>Zero Preprocessing Leakage</span>
            </div>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: 'var(--space-2)', lineHeight: 1.6 }}>
              All feature transformations and standard scalers are fitted exclusively on the training split of the respective fold, and applied downstream to validation and holdout splits.
            </div>
          </div>
        </div>
      </div>

      {/* Target Mathematical Formulations */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
        <div style={{ fontSize: 'var(--font-lg)', fontWeight: 700, color: 'var(--text-primary)' }}>
          2. Forecasting Target Formulations
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', fontSize: 'var(--font-sm)', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          <div style={{ padding: 'var(--space-3) var(--space-4)', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)' }}>
            <b style={{ color: 'var(--accent-temp)' }}>Target A: Next-Day Temperature (°C)</b> — Continuous regression predicting station average surface temperature at $t+1$ given historical telemetry up to cutoff $t$.
          </div>
          <div style={{ padding: 'var(--space-3) var(--space-4)', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)' }}>
            <b style={{ color: 'var(--accent-rain)' }}>Target B: Next-Day Rainfall Amount (mm)</b> — Continuous non-negative regression predicting precipitation volume at $t+1$ using a $\log(1+R)$ target transformation to compress extreme monsoon positive skewness.
          </div>
          <div style={{ padding: 'var(--space-3) var(--space-4)', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)' }}>
            <b style={{ color: 'var(--accent-primary)' }}>Target C: Next-Day Rain / No-Rain (Binary)</b> — Binary classification discriminating whether precipitation at $t+1$ is strictly zero ($y=0$) or positive ($y=1$), evaluated via ROC-AUC and PR-AUC.
          </div>
        </div>
      </div>

      {/* Database & Production Architecture */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Database size={20} style={{ color: 'var(--accent-primary)' }} />
          <div style={{ fontSize: 'var(--font-lg)', fontWeight: 700, color: 'var(--text-primary)' }}>
            3. End-to-End System Architecture
          </div>
        </div>

        <div style={{
          background: 'var(--bg-surface-elevated)',
          padding: 'var(--space-4)',
          borderRadius: 'var(--radius-md)',
          fontFamily: 'var(--font-mono)',
          fontSize: 'var(--font-xs)',
          color: 'var(--text-primary)',
          lineHeight: 1.6
        }}>
          ┌────────────────────────────────────────────────────────┐<br />
          │ React 19 + TypeScript Frontend (Phase 4 Active)        │<br />
          └───────────────────────────┬────────────────────────────┘<br />
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│ Future REST / WebSocket<br />
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br />
          ┌────────────────────────────────────────────────────────┐<br />
          │ FastAPI ML Inference Backend (Phase 8 Architecture)    │<br />
          │ - XGBoost C++ Runtime (&lt;0.1ms Latency)                │<br />
          │ - PyTorch LSTM Sequence Inference Service              │<br />
          └───────────────────────────┬────────────────────────────┘<br />
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│ Secured Connection Pool<br />
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br />
          ┌────────────────────────────────────────────────────────┐<br />
          │ MongoDB Application Database (Phase 4 Foundation)      │<br />
          │ - stations, weather_observations, forecast_results     │<br />
          └────────────────────────────────────────────────────────┘
        </div>
      </div>
    </div>
  );
};
