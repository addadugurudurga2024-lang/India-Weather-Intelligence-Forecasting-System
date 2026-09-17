import React, { useEffect, useState } from 'react';
import { CloudSun, MapPin, Calendar, CheckCircle } from 'lucide-react';
import { GlobalFilterBar } from '../components/filters/GlobalFilterBar';
import { MetricCard } from '../components/common/MetricCard';
import { PreviewBanner } from '../components/common/PreviewBanner';
import { TemperatureTrendChart } from '../components/charts/TemperatureTrendChart';
import { RainfallBarChart } from '../components/charts/RainfallBarChart';
import { analyticsService, weatherService } from '../services';
import { stations } from '../data';
import { useFilters } from '../context/FilterContext';
import type { DashboardKPI, WeatherObservation } from '../types';

export const DashboardPage: React.FC = () => {
  const { filters } = useFilters();
  const [kpis, setKpis] = useState<DashboardKPI[]>([]);
  const [observations, setObservations] = useState<WeatherObservation[]>([]);
  const [latestObs, setLatestObs] = useState<WeatherObservation | null>(null);

  const activeStation = filters.stationId !== 'ALL' 
    ? stations.find((s) => s.station_id === filters.stationId) || null 
    : null;

  useEffect(() => {
    analyticsService.getDashboardKPIs().then(setKpis);
  }, []);

  useEffect(() => {
    weatherService.getObservations(filters).then((obs) => {
      setObservations(obs);
      if (filters.stationId !== 'ALL') {
        weatherService.getLatestObservation(filters.stationId).then(setLatestObs);
      } else if (obs.length > 0) {
        setLatestObs(obs[0]);
      } else {
        setLatestObs(null);
      }
    });
  }, [filters]);

  const scopeTitle = activeStation 
    ? activeStation.station_name 
    : filters.district !== 'ALL'
    ? `${filters.district} Weather Scope`
    : filters.state !== 'ALL'
    ? `State Scope: ${filters.state}`
    : 'National Weather Scope (India Hub)';

  const scopeBadge = activeStation
    ? `${activeStation.district}, ${activeStation.state}`
    : filters.district !== 'ALL'
    ? `${filters.district}, ${filters.state}`
    : filters.state !== 'ALL'
    ? `${filters.state} Regional Scope`
    : 'Pan-India Overview';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Dev Preview Banner */}
      <PreviewBanner />

      {/* Global Filter Bar */}
      <GlobalFilterBar />

      {/* Current Weather Intelligence Hub */}
      <div className="card" style={{
        background: 'linear-gradient(135deg, color-mix(in srgb, var(--accent-primary) 10%, var(--bg-surface)) 0%, var(--bg-surface) 100%)',
        border: '1px solid var(--border-base)',
        padding: 'var(--space-6)'
      }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-4)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
            <div style={{
              width: '56px',
              height: '56px',
              borderRadius: 'var(--radius-lg)',
              background: 'linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-rain) 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#090d16',
              boxShadow: 'var(--shadow-glow-blue)'
            }}>
              <CloudSun size={32} strokeWidth={2.2} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                <span style={{ fontSize: 'var(--font-xl)', fontWeight: 800, color: 'var(--text-primary)' }}>
                  {scopeTitle}
                </span>
                <span className="badge badge-primary">
                  {scopeBadge}
                </span>
              </div>
              <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginTop: 'var(--space-1)' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Calendar size={13} />
                  <span>Observation Cutoff: <b>{latestObs?.date_of_record || '2025-02-10'}</b></span>
                </span>
                {activeStation && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <MapPin size={13} />
                    <span>Elevation: <b>{activeStation.elevation_m}m</b></span>
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Quick Metrics Capsule */}
          {latestObs && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', flexWrap: 'wrap' }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600 }}>Surface Temp</div>
                <div style={{ fontSize: 'var(--font-2xl)', fontWeight: 800, color: 'var(--accent-temp)', fontFamily: 'var(--font-mono)' }}>
                  {latestObs.avg_temp !== null ? `${latestObs.avg_temp}°C` : 'N/A'}
                </div>
              </div>

              <div style={{ height: '36px', width: '1px', background: 'var(--border-subtle)' }} />

              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600 }}>24h Rainfall</div>
                <div style={{ fontSize: 'var(--font-2xl)', fontWeight: 800, color: 'var(--accent-rain)', fontFamily: 'var(--font-mono)' }}>
                  {latestObs.rainfall !== null ? `${latestObs.rainfall} mm` : 'Missing'}
                </div>
              </div>

              <div style={{ height: '36px', width: '1px', background: 'var(--border-subtle)' }} />

              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600 }}>Wind / Pressure</div>
                <div style={{ fontSize: 'var(--font-sm)', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
                  {latestObs.wind_speed ?? '-'} km/h • {latestObs.air_pressure ?? '-'} hPa
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* KPI Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: 'var(--space-4)'
      }}>
        {kpis.map((kpi) => (
          <MetricCard
            key={kpi.id}
            title={kpi.title}
            value={kpi.value}
            unit={kpi.unit}
            subtext={kpi.subtext}
            status={kpi.status}
            sparklineData={kpi.sparklineData}
          />
        ))}
      </div>

      {/* Primary Visualizations Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(480px, 1fr))',
        gap: 'var(--space-6)'
      }}>
        {/* Temperature Trend Area */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: 'var(--font-base)', fontWeight: 700, color: 'var(--text-primary)' }}>
                Temperature Envelope &amp; Mean Curve
              </div>
              <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)' }}>
                Min/Max diurnal range shading with daily average trend (°C)
              </div>
            </div>
            <span className="badge badge-temp">Diurnal Envelope</span>
          </div>
          <TemperatureTrendChart data={observations} height={280} />
        </div>

        {/* Rainfall Distribution Area */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: 'var(--font-base)', fontWeight: 700, color: 'var(--text-primary)' }}>
                Precipitation Regime (Daily Rainfall)
              </div>
              <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)' }}>
                Verified dry days (0.0mm) vs active precipitation (&gt;0mm)
              </div>
            </div>
            <span className="badge badge-rain">Zero-Heavy Safe</span>
          </div>
          <RainfallBarChart data={observations} height={280} />
        </div>
      </div>

      {/* Model Status & Production Architecture Banner */}
      <div className="card" style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 'var(--space-4)',
        background: 'var(--bg-surface-elevated)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--accent-success-subtle)',
            color: 'var(--accent-success)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <CheckCircle size={22} />
          </div>
          <div>
            <div style={{ fontSize: 'var(--font-sm)', fontWeight: 700, color: 'var(--text-primary)' }}>
              Production Candidate: XGBoost Tabular GBDT
            </div>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)' }}>
              Holdout Temp MAE: <b>0.6527°C</b> • Rain Holdout Acc: <b>89.19%</b> • Sub-millisecond latency (&lt;0.1ms)
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          <span className="badge badge-primary">Fold 1 Verified</span>
          <span className="badge badge-primary">Fold 2 Verified</span>
          <span className="badge badge-purple">LSTM Benchmarked</span>
        </div>
      </div>
    </div>
  );
};
