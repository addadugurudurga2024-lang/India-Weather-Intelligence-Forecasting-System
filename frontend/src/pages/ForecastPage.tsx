import React, { useEffect, useState } from 'react';
import { CloudSun, Droplets, Thermometer, CheckCircle } from 'lucide-react';
import { PreviewBanner } from '../components/common/PreviewBanner';
import { forecastService } from '../services';
import { RainRiskWidget, WeatherAlertWidget, ModelExplanationWidget } from '../components/weather/WeatherIntelligenceWidgets';
import { OperationalTimeline25Day } from '../components/weather/OperationalTimeline25Day';
import { CurrentConditionsD0Panel } from '../components/weather/CurrentConditionsD0Panel';
import { ForecastDegradationChart } from '../components/weather/ForecastDegradationChart';
import { ModelTransparencyDrawer } from '../components/weather/ModelTransparencyDrawer';
import type { ForecastResult, Operational25DayTimeline, MultiHorizonSummary } from '../types';

export const ForecastPage: React.FC = () => {
  const [forecasts, setForecasts] = useState<ForecastResult[]>([]);
  const [selectedStationId, setSelectedStationId] = useState<string>('new_delhi_safdarjung_28.5833_77.2000_211m');
  const [selectedState, setSelectedState] = useState<string>('ALL');
  const [selectedDistrict, setSelectedDistrict] = useState<string>('ALL');
  const [timelineMode, setTimelineMode] = useState<'historical_holdout_replay' | 'operational_current'>('historical_holdout_replay');
  const [timeline, setTimeline] = useState<Operational25DayTimeline | null>(null);
  const [summary, setSummary] = useState<MultiHorizonSummary | null>(null);
  const [isLoadingTimeline, setIsLoadingTimeline] = useState<boolean>(true);
  const [timelineError, setTimelineError] = useState<string | null>(null);

  // Authoritative dynamic current date
  const todayStr = React.useMemo(() => {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  }, []);

  useEffect(() => {
    forecastService.getAllForecasts().then((res) => {
      setForecasts(res);
      if (res.length > 0) {
        setSelectedStationId((curr) => {
          const match = res.find((f) => f.station_id === curr || f.station_id.startsWith('new_delhi_safdarjung'));
          return match ? match.station_id : res[0].station_id;
        });
      }
    });

    forecastService.getMultiHorizonSummary().then((s) => setSummary(s));
  }, []);

  // Fetch timeline whenever selectedStationId or timelineMode changes
  useEffect(() => {
    let isCancelled = false;
    setIsLoadingTimeline(true);
    setTimelineError(null);

    forecastService.get25DayTimeline(selectedStationId, timelineMode)
      .then((res) => {
        if (!isCancelled) {
          if (res) {
            setTimeline(res);
          } else {
            setTimelineError(`Timeline unavailable for station ${selectedStationId}.`);
          }
          setIsLoadingTimeline(false);
        }
      })
      .catch((err) => {
        if (!isCancelled) {
          setTimelineError(err?.message || 'Failed to retrieve operational timeline.');
          setIsLoadingTimeline(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [selectedStationId, timelineMode]);

  const uniqueStates = React.useMemo(() => {
    return Array.from(new Set(forecasts.map((f) => f.state))).sort();
  }, [forecasts]);

  const uniqueDistricts = React.useMemo(() => {
    const subset = selectedState === 'ALL' ? forecasts : forecasts.filter((f) => f.state === selectedState);
    return Array.from(new Set(subset.map((f) => f.district))).sort();
  }, [forecasts, selectedState]);

  const filteredForecasts = React.useMemo(() => {
    return forecasts.filter((f) => {
      if (selectedState !== 'ALL' && f.state !== selectedState) return false;
      if (selectedDistrict !== 'ALL' && f.district !== selectedDistrict) return false;
      return true;
    });
  }, [forecasts, selectedState, selectedDistrict]);

  // Synchronize active station whenever filter changes to avoid stale station retention
  const handleStateChange = (newState: string) => {
    setSelectedState(newState);
    setSelectedDistrict('ALL');
    setTimeline(null); // Clear stale timeline immediately
    setIsLoadingTimeline(true);
    setTimelineError(null);

    const subset = newState === 'ALL' ? forecasts : forecasts.filter((f) => f.state === newState);
    if (subset.length > 0) {
      setSelectedStationId(subset[0].station_id);
    }
  };

  const handleDistrictChange = (newDistrict: string) => {
    setSelectedDistrict(newDistrict);
    setTimeline(null); // Clear stale timeline immediately
    setIsLoadingTimeline(true);
    setTimelineError(null);

    const subset = forecasts.filter((f) => {
      if (selectedState !== 'ALL' && f.state !== selectedState) return false;
      if (newDistrict !== 'ALL' && f.district !== newDistrict) return false;
      return true;
    });
    if (subset.length > 0) {
      setSelectedStationId(subset[0].station_id);
    }
  };

  const handleStationChange = (newStationId: string) => {
    setSelectedStationId(newStationId);
    setTimeline(null); // Clear stale timeline immediately
    setIsLoadingTimeline(true);
    setTimelineError(null);
  };

  const handleModeChange = (newMode: 'historical_holdout_replay' | 'operational_current') => {
    setTimelineMode(newMode);
    setTimeline(null); // Clear stale timeline immediately
    setIsLoadingTimeline(true);
    setTimelineError(null);
  };

  // Ensure active forecast strictly matches selectedStationId
  const activeForecast = forecasts.find((f) => f.station_id === selectedStationId) || null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <PreviewBanner
        message="Phase 8.5 Operational Weather Intelligence Center"
        subtext="25-Day Continuous Timeline (12 Days Historical / Model Context • Today D0 • 12 Days Model Forecasts) across all 413 canonical monitoring stations."
      />

      {/* Operational Mode & Canonical Station Selector Card */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-3)' }}>
          <div>
            <div style={{ fontSize: 'var(--font-sm)', fontWeight: 800, color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Operational Scope & Station Filter
            </div>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Select operational timeline mode and canonical station. All downstream cards, D0 conditions, and timeline dynamically synchronize.
            </div>
          </div>

          {/* Mode Switcher */}
          <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
            <button
              onClick={() => handleModeChange('historical_holdout_replay')}
              className={`btn btn-sm ${timelineMode === 'historical_holdout_replay' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '11px', fontWeight: timelineMode === 'historical_holdout_replay' ? 700 : 500 }}
            >
              Audited Replay (D0: 2025-01-20)
            </button>
            <button
              onClick={() => handleModeChange('operational_current')}
              className={`btn btn-sm ${timelineMode === 'operational_current' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '11px', fontWeight: timelineMode === 'operational_current' ? 700 : 500 }}
            >
              Current Operational (D0: {todayStr})
            </button>
          </div>
        </div>

        {/* Filter Selectors */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 'var(--space-3)',
          padding: 'var(--space-4)',
          background: 'var(--bg-surface-elevated)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)',
        }}>
          <div>
            <label style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-tertiary)', marginBottom: '6px', display: 'block' }}>
              State:
            </label>
            <select
              className="select"
              style={{ width: '100%', padding: '6px 10px', fontSize: 'var(--font-sm)' }}
              value={selectedState}
              onChange={(e) => handleStateChange(e.target.value)}
              aria-label="Select State"
            >
              <option value="ALL">All States ({uniqueStates.length})</option>
              {uniqueStates.map((st) => (
                <option key={st} value={st}>{st}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-tertiary)', marginBottom: '6px', display: 'block' }}>
              District:
            </label>
            <select
              className="select"
              style={{ width: '100%', padding: '6px 10px', fontSize: 'var(--font-sm)' }}
              value={selectedDistrict}
              onChange={(e) => handleDistrictChange(e.target.value)}
              aria-label="Select District"
            >
              <option value="ALL">All Districts ({uniqueDistricts.length})</option>
              {uniqueDistricts.map((dist) => (
                <option key={dist} value={dist}>{dist}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-tertiary)', marginBottom: '6px', display: 'block' }}>
              Canonical Station:
            </label>
            <select
              className="select"
              style={{ width: '100%', padding: '6px 10px', fontSize: 'var(--font-sm)' }}
              value={selectedStationId}
              onChange={(e) => handleStationChange(e.target.value)}
              aria-label="Select Station"
            >
              {filteredForecasts.map((stn) => (
                <option key={stn.station_id} value={stn.station_id}>
                  {stn.station_name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Loading Skeleton State */}
      {isLoadingTimeline && (
        <div className="card" style={{ padding: 'var(--space-6)', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--space-3)' }}>
          <div className="animate-spin" style={{ width: '28px', height: '28px', border: '3px solid var(--border-subtle)', borderTopColor: 'var(--accent-primary)', borderRadius: '50%' }} />
          <div style={{ fontWeight: 800, fontSize: 'var(--font-base)', color: 'var(--text-primary)' }}>
            Retrieving 25-Day Operational Timeline...
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)' }}>
            Syncing canonical station state for <strong>{selectedStationId}</strong> in {timelineMode === 'historical_holdout_replay' ? 'Audited Ground-Truth Replay (2025-01-20)' : `Current Operational Mode (${todayStr})`}. Stale station data cleared.
          </div>
        </div>
      )}

      {/* Error State */}
      {!isLoadingTimeline && timelineError && (
        <div className="card" style={{ borderLeft: '4px solid var(--accent-danger)', background: 'rgba(239, 68, 68, 0.05)', padding: 'var(--space-4)' }}>
          <div style={{ fontWeight: 800, fontSize: 'var(--font-base)', color: 'var(--text-primary)' }}>
            Operational Timeline Unavailable
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '4px' }}>
            {timelineError}
          </div>
        </div>
      )}

      {/* 1. D0 Current Conditions Panel */}
      {!isLoadingTimeline && timeline && (
        <CurrentConditionsD0Panel timelineData={timeline} timelineMode={timelineMode} />
      )}

      {/* 2. Operational 25-Day Continuous Timeline Strip */}
      {!isLoadingTimeline && timeline && (
        <OperationalTimeline25Day timelineData={timeline} timelineMode={timelineMode} />
      )}

      {/* 3. Forecast Skill Degradation Chart */}
      {!isLoadingTimeline && summary && (
        <ForecastDegradationChart summary={summary} />
      )}

      {/* 4. Scientific Transparency & Model Ledger */}
      {!isLoadingTimeline && timeline && summary && (
        <ModelTransparencyDrawer timeline={timeline} summary={summary} />
      )}

      {/* 5. Legacy Tri-Target Cards & Intelligence Widgets */}
      {!isLoadingTimeline && activeForecast && activeForecast.station_id === selectedStationId && (
        <>
          <div className="card" style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-base)',
            padding: 'var(--space-6)'
          }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-4)' }}>
              <div>
                <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
                  <span className="badge badge-primary">
                    Target Horizon: {activeForecast.forecast_date} (T+1 Point Forecast)
                  </span>
                  <span className="badge badge-neutral" style={{ border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)' }}>
                    LEGACY / HISTORICAL PHASE 3 REFERENCE
                  </span>
                </div>
                <div style={{ fontSize: 'var(--font-2xl)', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
                  {activeForecast.station_name} Next-Day Synopsis
                </div>
                <div style={{ fontSize: 'var(--font-sm)', color: 'var(--text-secondary)' }}>
                  {activeForecast.district}, {activeForecast.state} &bull; Generated at: {activeForecast.generated_at}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                <div className="badge badge-success" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <CheckCircle size={13} />
                  <span>XGBoost Multi-Horizon v1 Validated</span>
                </div>
              </div>
            </div>

            {/* Tri-Target Metric Cards */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
              gap: 'var(--space-4)',
              marginTop: 'var(--space-6)'
            }}>
              {/* Target A: Temperature */}
              <div style={{
                background: 'var(--bg-surface-glass)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--space-5)',
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--space-2)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                    Target A: Next-Day Temperature
                  </span>
                  <Thermometer size={18} style={{ color: 'var(--accent-temp)' }} />
                </div>
                <div style={{ fontSize: 'var(--font-4xl)', fontWeight: 800, color: 'var(--accent-temp)', fontFamily: 'var(--font-mono)' }}>
                  {activeForecast.predicted_temp}°C
                </div>
                <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)' }}>
                  Model: {activeForecast.model_temperature}
                </div>
              </div>

              {/* Target B: Rainfall Amount */}
              <div style={{
                background: 'var(--bg-surface-glass)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--space-5)',
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--space-2)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                    Target B: Next-Day Rainfall
                  </span>
                  <Droplets size={18} style={{ color: 'var(--accent-rain)' }} />
                </div>
                <div style={{ fontSize: 'var(--font-4xl)', fontWeight: 800, color: 'var(--accent-rain)', fontFamily: 'var(--font-mono)' }}>
                  {activeForecast.predicted_rainfall_amount} mm
                </div>
                <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)' }}>
                  Model: {activeForecast.model_rainfall}
                </div>
              </div>

              {/* Target C: Rain Probability */}
              <div style={{
                background: 'var(--bg-surface-glass)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--space-5)',
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--space-2)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                    Target C: Rain Occurrence
                  </span>
                  <CloudSun size={18} style={{ color: 'var(--accent-warning)' }} />
                </div>
                <div style={{ fontSize: 'var(--font-4xl)', fontWeight: 800, color: 'var(--accent-warning)', fontFamily: 'var(--font-mono)' }}>
                  {Math.round(activeForecast.predicted_rain_probability * 100)}%
                </div>
                <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)' }}>
                  Classification: {activeForecast.predicted_rain_binary ? 'Rain Likely (prob >= 0.30)' : 'Dry Day (prob < 0.30)'}
                </div>
              </div>
            </div>
          </div>

          {/* Intelligence Foundation Widgets */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: 'var(--space-4)'
          }}>
            <RainRiskWidget
              probability={activeForecast.predicted_rain_probability}
              predictedAmountMm={activeForecast.predicted_rainfall_amount}
            />
            <WeatherAlertWidget
              stationName={activeForecast.station_name}
              tempC={activeForecast.predicted_temp}
              rainMm={activeForecast.predicted_rainfall_amount}
            />
            <ModelExplanationWidget
              modelName={activeForecast.model_temperature}
            />
          </div>
        </>
      )}
    </div>
  );
};
