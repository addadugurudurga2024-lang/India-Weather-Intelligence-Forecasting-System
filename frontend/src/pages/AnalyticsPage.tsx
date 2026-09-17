import React, { useEffect, useState } from 'react';
import { Thermometer, ArrowUp, ArrowDown, Activity } from 'lucide-react';
import { GlobalFilterBar } from '../components/filters/GlobalFilterBar';
import { PreviewBanner } from '../components/common/PreviewBanner';
import { MetricCard } from '../components/common/MetricCard';
import { TemperatureTrendChart } from '../components/charts/TemperatureTrendChart';
import { weatherService } from '../services';
import { useFilters } from '../context/FilterContext';
import type { WeatherObservation } from '../types';

export const AnalyticsPage: React.FC = () => {
  const { filters } = useFilters();
  const [observations, setObservations] = useState<WeatherObservation[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    setIsLoading(true);
    setObservations([]); // Invalidate stale scope immediately
    weatherService.getScopedTimeseries(filters, 365)
      .then((data) => {
        setObservations(data);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [filters]);

  const validTemps = observations.filter((o) => o.avg_temp !== null).map((o) => o.avg_temp as number);
  const maxTemps = observations.filter((o) => o.max_temp !== null).map((o) => o.max_temp as number);
  const minTemps = observations.filter((o) => o.min_temp !== null).map((o) => o.min_temp as number);

  const meanTemp = validTemps.length > 0 ? (validTemps.reduce((a, b) => a + b, 0) / validTemps.length).toFixed(1) : '--';
  const highestMax = maxTemps.length > 0 ? Math.max(...maxTemps).toFixed(1) : '--';
  const lowestMin = minTemps.length > 0 ? Math.min(...minTemps).toFixed(1) : '--';
  const diurnalSpread = (validTemps.length > 0 && maxTemps.length > 0 && minTemps.length > 0)
    ? (parseFloat(highestMax) - parseFloat(lowestMin)).toFixed(1)
    : '--';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <PreviewBanner message="Temperature Climatology &amp; Multivariate Analytics" subtext="Calculated from canonical Phase 2 observations across reporting physical stations." />
      <GlobalFilterBar />

      {/* Analytics KPI Header */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: 'var(--space-4)'
      }}>
        <MetricCard
          title="Period Mean Temperature"
          value={meanTemp}
          unit={meanTemp !== '--' ? '°C' : ''}
          subtext="Harmonized daily mean"
          status="normal"
          icon={Thermometer}
        />
        <MetricCard
          title="Peak Observed High"
          value={highestMax}
          unit={highestMax !== '--' ? '°C' : ''}
          subtext="Maximum daily surface reading"
          status="warning"
          icon={ArrowUp}
        />
        <MetricCard
          title="Lowest Observed Low"
          value={lowestMin}
          unit={lowestMin !== '--' ? '°C' : ''}
          subtext="Minimum night-time surface reading"
          status="info"
          icon={ArrowDown}
        />
        <MetricCard
          title="Total Temperature Range"
          value={diurnalSpread}
          unit={diurnalSpread !== '--' ? '°C' : ''}
          subtext="Extremes span across active scope"
          status="normal"
          icon={Activity}
        />
      </div>

      {/* Main Temperature Chart */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: 'var(--font-lg)', fontWeight: 800, color: 'var(--text-primary)' }}>
              Interactive Surface Temperature Timeseries
            </div>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)' }}>
              {isLoading ? 'Loading canonical observations...' : `Displaying ${observations.length} chronological points for active scope`}
            </div>
          </div>
          <span className="badge badge-temp">Diurnal Envelope</span>
        </div>

        {isLoading ? (
          <div style={{ height: 380, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
            Loading temperature records...
          </div>
        ) : observations.length === 0 ? (
          <div style={{ height: 380, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '8px', color: 'var(--text-tertiary)' }}>
            <div style={{ fontWeight: 600, fontSize: 'var(--font-base)' }}>NO DATA FOR SELECTED SCOPE</div>
            <div style={{ fontSize: 'var(--font-xs)' }}>No canonical temperature telemetry matches the specified state, district, or station filters.</div>
          </div>
        ) : (
          <TemperatureTrendChart data={observations} height={380} />
        )}
      </div>

      {/* Station Temperature Climatology Breakdown */}
      <div className="card">
        <div style={{ fontSize: 'var(--font-base)', fontWeight: 700, color: 'var(--text-primary)', marginBottom: 'var(--space-4)' }}>
          Temperature Distribution by Regional Zone
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-4)' }}>
          <div style={{ padding: 'var(--space-4)', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ fontWeight: 700, fontSize: 'var(--font-sm)', color: 'var(--accent-primary)' }}>Northern Plains (Indo-Gangetic)</div>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Continental winter regime. Rapid diurnal cooling with overnight lows below 8°C.
            </div>
          </div>
          <div style={{ padding: 'var(--space-4)', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ fontWeight: 700, fontSize: 'var(--font-sm)', color: 'var(--accent-rain)' }}>Peninsular &amp; Coastal</div>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Maritime moderating effect. Diurnal spread compressed to &lt;6°C with constant humidity.
            </div>
          </div>
          <div style={{ padding: 'var(--space-4)', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ fontWeight: 700, fontSize: 'var(--font-sm)', color: '#c084fc' }}>High-Elevation Himalayan</div>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Sub-zero freeze vulnerability. Elevation lapse rate averages ~6.5°C per 1,000m.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
