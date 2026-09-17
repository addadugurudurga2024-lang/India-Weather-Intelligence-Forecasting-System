import React, { useEffect, useState } from 'react';
import { CloudRain, Droplets, Sun, AlertTriangle } from 'lucide-react';
import { GlobalFilterBar } from '../components/filters/GlobalFilterBar';
import { PreviewBanner } from '../components/common/PreviewBanner';
import { MetricCard } from '../components/common/MetricCard';
import { RainfallBarChart } from '../components/charts/RainfallBarChart';
import { weatherService } from '../services';
import { useFilters } from '../context/FilterContext';
import type { WeatherObservation } from '../types';

export const RainfallPage: React.FC = () => {
  const { filters } = useFilters();
  const [observations, setObservations] = useState<WeatherObservation[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    setIsLoading(true);
    setObservations([]); // Invalidate stale scope immediately
    // Use scoped timeseries so date-aggregated or station-level sequence is retrieved
    weatherService.getScopedTimeseries(filters, 365)
      .then((data) => {
        setObservations(data);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [filters]);

  const hasData = observations.length > 0;
  const validRain = observations.filter((o) => o.rainfall !== null).map((o) => o.rainfall as number);
  const totalRain = validRain.reduce((a, b) => a + b, 0);
  const avgRain = hasData && validRain.length > 0 ? (totalRain / validRain.length).toFixed(2) : '--';
  
  const rainyDays = validRain.filter((r) => r > 0).length;
  const dryDays = validRain.filter((r) => r === 0).length;
  const missingDays = observations.filter((o) => o.rainfall === null).length;

  const rainyRatio = hasData && validRain.length > 0 ? ((rainyDays / validRain.length) * 100).toFixed(1) : '--';
  const peakRain = hasData && validRain.length > 0 ? Math.max(...validRain).toFixed(1) : '--';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <PreviewBanner message="Precipitation Intelligence &amp; Zero-Heavy Regime Audit" subtext="Strictly adheres to Project Principle 2.3: missing rainfall gauge observations are preserved as null and never converted to zero." />
      <GlobalFilterBar />

      {/* KPI Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: 'var(--space-4)'
      }}>
        <MetricCard
          title="Average Daily Rainfall"
          value={avgRain}
          unit={avgRain !== '--' ? 'mm' : ''}
          subtext={hasData ? "Mean across valid reporting days" : "No reporting data"}
          status="info"
          icon={Droplets}
        />
        <MetricCard
          title="Active Rain Occurrence"
          value={rainyRatio !== '--' ? `${rainyRatio}%` : '--'}
          subtext={hasData ? `${rainyDays.toLocaleString()} rain days vs ${dryDays.toLocaleString()} dry days` : "No reporting data"}
          status="normal"
          icon={CloudRain}
        />
        <MetricCard
          title="Peak 24h Shower"
          value={peakRain}
          unit={peakRain !== '--' ? 'mm' : ''}
          subtext={hasData ? "Maximum single-event reading" : "No reporting data"}
          status="warning"
          icon={Droplets}
        />
        <MetricCard
          title="Missing Gauge Days"
          value={hasData ? missingDays : '--'}
          unit={hasData ? "Days" : ''}
          subtext="Preserved nulls (zero-imputation rejected)"
          status="normal"
          icon={Sun}
        />
      </div>

      {/* Primary Rainfall Bar Chart */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: 'var(--font-lg)', fontWeight: 800, color: 'var(--text-primary)' }}>
              Daily Precipitation Sequence
            </div>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)' }}>
              {isLoading ? 'Loading canonical rainfall telemetry...' : `Cyan bars indicate active rain events (>0.0mm); muted bars indicate verified dry observations (${observations.length} days)`}
            </div>
          </div>
          <span className="badge badge-rain">Zero-Heavy Audited</span>
        </div>

        {isLoading ? (
          <div style={{ height: 360, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
            Loading rainfall records...
          </div>
        ) : observations.length === 0 ? (
          <div style={{ height: 360, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '8px', color: 'var(--text-tertiary)' }}>
            <div style={{ fontWeight: 600, fontSize: 'var(--font-base)' }}>NO DATA FOR SELECTED SCOPE</div>
            <div style={{ fontSize: 'var(--font-xs)' }}>No canonical rainfall telemetry matches the specified state, district, or station filters.</div>
          </div>
        ) : (
          <RainfallBarChart data={observations} height={360} />
        )}
      </div>

      {/* Scientific Note on Rainfall Modeling */}
      <div className="card" style={{
        borderLeft: '4px solid var(--accent-warning)',
        display: 'flex',
        alignItems: 'flex-start',
        gap: 'var(--space-4)'
      }}>
        <div style={{ color: 'var(--accent-warning)', marginTop: '2px' }}>
          <AlertTriangle size={24} />
        </div>
        <div>
          <div style={{ fontSize: 'var(--font-sm)', fontWeight: 700, color: 'var(--text-primary)' }}>
            Scientific Precaution: Extreme Rainfall Skewness &amp; Target Transformation
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: 1.6 }}>
            In Indian monsoon meteorology, precipitation is heavily zero-inflated (over 55% dry observations nationally during monsoon, and &gt;90% in winter) with extreme positive skewness (&gt;100mm/day cloudbursts). As verified in Phase 3 Task 09/14, applying a direct <code style={{ fontFamily: 'var(--font-mono)', background: 'var(--bg-surface-elevated)', padding: '1px 4px', borderRadius: '4px' }}>log1p</code> transformation (<code style={{ fontFamily: 'var(--font-mono)' }}>log(1+R)</code>) allows regressors to compress heavy tails while preserving exact dry zeros.
          </div>
        </div>
      </div>
    </div>
  );
};
