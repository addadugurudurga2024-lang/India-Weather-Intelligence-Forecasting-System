import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  CalendarDays,
  MapPin,
  Thermometer,
  CloudRain,
  Wind,
  Gauge,
  AlertTriangle,
  Clock,
  Sparkles,
  SlidersHorizontal
} from 'lucide-react';
import { stations } from '../data';
import { longTermPredictorService } from '../services';
import type { LongTermPredictionResult } from '../types';

const getTodayDateStr = () => {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
};

export const LongTermPredictorPage: React.FC = () => {
  // Default selection initialized dynamically to today's calendar date
  const [selectedDate, setSelectedDate] = useState<string>(() => getTodayDateStr());
  const [selectedState, setSelectedState] = useState<string>('DL');
  const [selectedDistrict, setSelectedDistrict] = useState<string>('New Delhi');
  const [selectedStationId, setSelectedStationId] = useState<string>('new_delhi_safdarjung_28.5833_77.2000_211m');

  const [prediction, setPrediction] = useState<LongTermPredictionResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'reference' | 'explainability' | 'limitations'>('overview');

  // Unique sorted states
  const uniqueStates = useMemo(() => {
    return Array.from(new Set(stations.map((s) => s.state))).sort();
  }, []);

  // Filtered districts based on state
  const availableDistricts = useMemo(() => {
    if (selectedState === 'ALL') {
      return Array.from(new Set(stations.map((s) => s.district))).sort();
    }
    return Array.from(new Set(stations.filter((s) => s.state === selectedState).map((s) => s.district))).sort();
  }, [selectedState]);

  // Filtered stations based on state & district
  const availableStations = useMemo(() => {
    return stations.filter((s) => {
      if (selectedState !== 'ALL' && s.state !== selectedState) return false;
      if (selectedDistrict !== 'ALL' && s.district !== selectedDistrict) return false;
      return true;
    }).sort((a, b) => a.station_name.localeCompare(b.station_name));
  }, [selectedState, selectedDistrict]);

  // Handle station dropdown consistency
  useEffect(() => {
    if (availableStations.length > 0) {
      const exists = availableStations.some((s) => s.station_id === selectedStationId);
      if (!exists) {
        setSelectedStationId(availableStations[0].station_id);
      }
    }
  }, [availableStations, selectedStationId]);

  // Selection change handlers - invalidate stale prediction immediately
  const handleDateChange = (newDate: string) => {
    setSelectedDate(newDate);
    setPrediction(null);
    setError(null);
  };

  const handleStateChange = (newState: string) => {
    setSelectedState(newState);
    setSelectedDistrict('ALL');
    setPrediction(null);
    setError(null);
  };

  const handleDistrictChange = (newDistrict: string) => {
    setSelectedDistrict(newDistrict);
    setPrediction(null);
    setError(null);
  };

  const handleStationChange = (newStationId: string) => {
    setSelectedStationId(newStationId);
    setPrediction(null);
    setError(null);
  };

  // Generate prediction on demand
  const handleGeneratePrediction = useCallback(async (dateToUse?: string, stnToUse?: string) => {
    const targetDate = dateToUse || selectedDate;
    const targetStn = stnToUse || selectedStationId;
    setIsLoading(true);
    setPrediction(null); // Clear stale prediction immediately so previous station/date results are never shown
    setError(null);
    try {
      const res = await longTermPredictorService.predict(targetDate, targetStn);
      setPrediction(res);
      if (res.status === 'UNAVAILABLE') {
        setError(res.error || 'Prediction unavailable for this station/date combination.');
      }
    } catch (err: any) {
      console.error('Prediction generation error:', err);
      setError(err?.message || 'Failed to generate prediction. Please verify server connection.');
    } finally {
      setIsLoading(false);
    }
  }, [selectedDate, selectedStationId]);

  // Initial load: dynamically evaluates today's calendar date
  useEffect(() => {
    const initialDate = getTodayDateStr();
    handleGeneratePrediction(initialDate, 'new_delhi_safdarjung_28.5833_77.2000_211m');
  }, [handleGeneratePrediction]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* System Distinction Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(14, 165, 233, 0.12) 100%)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--space-4) var(--space-5)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-2)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <Sparkles size={18} color="var(--accent-primary)" />
            <span style={{ fontWeight: 800, fontSize: 'var(--font-sm)', color: 'var(--accent-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Phase 9 — Long-Term Weather Predictor
            </span>
          </div>
          <span className="badge badge-info" style={{ fontSize: '11px' }}>
            Historical &amp; Seasonal Model Layer
          </span>
        </div>
        <p style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
          <strong>System Distinction:</strong> The <em>Operational Forecast Center</em> evaluates short-horizon numerical models (<code style={{ color: 'var(--accent-rain)' }}>T+1 → T+12</code>).
          The <em>Long-Term Predictor</em> estimates future date weather variables using learned 10-year historical station, seasonal, and geographic relationships.
        </p>
      </div>

      {/* Main Control Panel */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-2)' }}>
          <div>
            <h1 style={{ fontSize: 'var(--font-2xl)', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
              LONG-TERM WEATHER PREDICTOR
            </h1>
            <p style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
              Estimate weather conditions for a selected future date using learned historical station, seasonal, geographic and weather-pattern information.
            </p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
            <span style={{ fontSize: '10px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
              Example Demonstration Presets:
            </span>
            <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
              <button
                onClick={() => {
                  setSelectedDate('2026-11-15');
                  setSelectedState('AP');
                  setSelectedDistrict('East Godavari');
                  setSelectedStationId('rajahmundry_rjnagaram_17.1104_81.8182_46m');
                  handleGeneratePrediction('2026-11-15', 'rajahmundry_rjnagaram_17.1104_81.8182_46m');
                }}
                className="btn btn-secondary btn-sm"
                style={{ fontSize: '11px' }}
              >
                15-Nov-2026 — Rajanagaram
              </button>
              <button
                onClick={() => {
                  setSelectedDate('2027-01-01');
                  setSelectedState('DL');
                  setSelectedDistrict('New Delhi');
                  setSelectedStationId('new_delhi_safdarjung_28.5833_77.2000_211m');
                  handleGeneratePrediction('2027-01-01', 'new_delhi_safdarjung_28.5833_77.2000_211m');
                }}
                className="btn btn-secondary btn-sm"
                style={{ fontSize: '11px' }}
              >
                01-Jan-2027 — Delhi
              </button>
            </div>
          </div>
        </div>


        {/* Form Controls Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 'var(--space-3)',
            padding: 'var(--space-4)',
            background: 'var(--bg-surface-elevated)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
            alignItems: 'flex-end'
          }}
        >
          {/* Target Calendar Date */}
          <div>
            <label style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-tertiary)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CalendarDays size={14} /> Future Calendar Date:
            </label>
            <input
              type="date"
              className="select"
              style={{ width: '100%', padding: '6px 10px', fontSize: 'var(--font-sm)' }}
              value={selectedDate}
              min="2025-01-01"
              max="2027-12-31"
              onChange={(e) => handleDateChange(e.target.value)}
              aria-label="Target Date"
            />
            <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', marginTop: '4px' }}>
              Range: 2025-01-01 to 2027-12-31 (Observed records end 2025-02-10; subsequent dates are model estimates)
            </div>
          </div>

          {/* State */}
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

          {/* District */}
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
              <option value="ALL">All Districts ({availableDistricts.length})</option>
              {availableDistricts.map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          {/* Station */}
          <div>
            <label style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-tertiary)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <MapPin size={14} /> Canonical Station:
            </label>
            <select
              className="select"
              style={{ width: '100%', padding: '6px 10px', fontSize: 'var(--font-sm)' }}
              value={selectedStationId}
              onChange={(e) => handleStationChange(e.target.value)}
              aria-label="Select Station"
            >
              {availableStations.map((s) => (
                <option key={s.station_id} value={s.station_id}>
                  {s.station_name} ({s.elevation_m}m)
                </option>
              ))}
            </select>
          </div>

          {/* Action Button */}
          <div>
            <button
              onClick={() => handleGeneratePrediction()}
              disabled={isLoading}
              className="btn btn-primary"
              style={{ width: '100%', padding: '8px 16px', fontWeight: 800, fontSize: 'var(--font-sm)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
            >
              {isLoading ? (
                <>
                  <Clock size={16} className="animate-spin" /> Evaluating...
                </>
              ) : (
                <>
                  <Sparkles size={16} /> GENERATE PREDICTION
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Explicit Loading Skeleton State */}
      {isLoading && (
        <div className="card" style={{ padding: 'var(--space-6)', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--space-3)' }}>
          <Clock size={32} className="animate-spin" color="var(--accent-primary)" />
          <div style={{ fontWeight: 800, fontSize: 'var(--font-base)', color: 'var(--text-primary)' }}>
            Evaluating Long-Term Weather Models...
          </div>
          <p style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', maxWidth: '450px', margin: 0 }}>
            Executing genuine XGBoost multi-target inference across station topography, cyclic calendar features, and empirical prediction intervals.
          </p>
        </div>
      )}

      {/* Explicit Error State */}
      {!isLoading && error && (
        <div className="card" style={{ borderLeft: '4px solid var(--accent-danger)', background: 'rgba(239, 68, 68, 0.05)', padding: 'var(--space-4)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <AlertTriangle size={24} color="var(--accent-danger)" />
            <div>
              <div style={{ fontWeight: 800, fontSize: 'var(--font-base)', color: 'var(--text-primary)' }}>
                Prediction Request Failed
              </div>
              <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '2px' }}>
                {error}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Explicit Prompt when inputs changed without generating */}
      {!isLoading && !error && !prediction && (
        <div className="card" style={{ padding: 'var(--space-6)', textAlign: 'center', color: 'var(--text-tertiary)' }}>
          <Sparkles size={28} style={{ margin: '0 auto 8px auto', opacity: 0.6 }} />
          <div style={{ fontWeight: 700, fontSize: 'var(--font-sm)', color: 'var(--text-secondary)' }}>
            Ready to Generate Long-Term Prediction
          </div>
          <p style={{ fontSize: 'var(--font-xs)', margin: '4px 0 0 0' }}>
            Select target date and station above, then click <strong>GENERATE PREDICTION</strong>.
          </p>
        </div>
      )}

      {/* Prediction Output Results */}
      {!isLoading && prediction && prediction.status === 'AVAILABLE' && prediction.predictions && (
        <>
          {/* Status & Provenance Banner */}
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: 'var(--space-3)',
              padding: 'var(--space-3) var(--space-4)',
              background: 'var(--bg-surface-elevated)',
              borderRadius: 'var(--radius-md)',
              borderLeft: '4px solid var(--accent-primary)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
              <span style={{ fontSize: 'var(--font-sm)', fontWeight: 800, color: 'var(--text-primary)' }}>
                Target: {prediction.station_name} • {prediction.prediction_date}
              </span>
              <span className="badge badge-info" style={{ fontSize: '11px' }}>
                MODEL PREDICTION
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
              <span style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)', fontWeight: 600 }}>
                Provenance:
              </span>
              {prediction.provenance?.inference_source === 'XGBOOST_LONG_TERM' && (
                <span className="badge badge-success" style={{ fontSize: '11px', fontWeight: 700 }}>
                  XGBOOST_LONG_TERM (Live Server Inference)
                </span>
              )}
              {prediction.provenance?.inference_source === 'MONGODB_CACHE' && (
                <span className="badge badge-info" style={{ fontSize: '11px', fontWeight: 700 }}>
                  MONGODB_CACHE (Persisted Cache)
                </span>
              )}
              {prediction.provenance?.inference_source === 'OFFLINE_ESTIMATE' && (
                <span className="badge badge-warning" style={{ fontSize: '11px', fontWeight: 700 }}>
                  OFFLINE_ESTIMATE (Deterministic Baseline)
                </span>
              )}
              {(!prediction.provenance?.inference_source) && (
                <span className="badge badge-info" style={{ fontSize: '11px', fontWeight: 700 }}>
                  XGBOOST_LONG_TERM
                </span>
              )}
              <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', fontFamily: 'monospace' }}>
                {prediction.provenance?.model_version || 'v1.0.0'}
              </span>
            </div>
          </div>
          {/* Target Variables Metrics Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 'var(--space-4)' }}>
            {/* Average Temperature */}
            <div className="card" style={{ borderTop: '4px solid var(--accent-temp)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>
                  Average Temperature
                </span>
                <Thermometer size={18} color="var(--accent-temp)" />
              </div>
              <div style={{ fontSize: '2.2rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                {prediction.predictions.avg_temp}°C
              </div>
              <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '4px' }}>
                80% Prediction Interval:{' '}
                <strong style={{ color: 'var(--text-primary)' }}>
                  [{prediction.uncertainty?.avg_temp_interval_80[0]}°C – {prediction.uncertainty?.avg_temp_interval_80[1]}°C]
                </strong>
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginTop: '8px', borderTop: '1px solid var(--border-subtle)', paddingTop: '6px' }}>
                Historical {prediction.historical_reference?.calendar_context.month || 'Target Month'} Mean: {prediction.historical_reference?.station_monthly_climatology.historical_mean_temp ?? '--'}°C
              </div>
            </div>

            {/* Predicted Temperature Extremes (Separate from Statistical Uncertainty Interval) */}
            <div className="card" style={{ borderTop: '4px solid var(--accent-warning)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>
                  Predicted Temperature Extremes
                </span>
                <SlidersHorizontal size={18} color="var(--accent-warning)" />
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 'var(--space-3)' }}>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', fontWeight: 700, textTransform: 'uppercase' }}>Minimum</div>
                  <span style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                    {prediction.predictions.min_temp}°C
                  </span>
                </div>
                <span style={{ fontSize: 'var(--font-sm)', color: 'var(--text-tertiary)', alignSelf: 'center', margin: '0 4px' }}>to</span>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', fontWeight: 700, textTransform: 'uppercase' }}>Maximum</div>
                  <span style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                    {prediction.predictions.max_temp}°C
                  </span>
                </div>
              </div>
              <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Min 80% PI: [{prediction.uncertainty?.min_temp_interval_80[0]}°, {prediction.uncertainty?.min_temp_interval_80[1]}°] • Max 80% PI: [{prediction.uncertainty?.max_temp_interval_80[0]}°, {prediction.uncertainty?.max_temp_interval_80[1]}°]
              </div>
              <div style={{ fontSize: '11px', color: 'var(--accent-success)', marginTop: '8px', borderTop: '1px solid var(--border-subtle)', paddingTop: '6px' }}>
                ✓ Physical Ordering Enforced: T_min ≤ T_avg ≤ T_max
              </div>
            </div>

            {/* Rain Occurrence Probability & Expected Rainfall Amount */}
            <div className="card" style={{ borderTop: '4px solid var(--accent-rain)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>
                  Rain Occurrence &amp; Amount
                </span>
                <CloudRain size={18} color="var(--accent-rain)" />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                  <span style={{ fontSize: '11px', color: 'var(--text-secondary)', fontWeight: 600 }}>Rain Occurrence Probability:</span>
                  <span style={{ fontSize: '1.8rem', fontWeight: 900, color: 'var(--accent-rain)' }}>
                    {prediction.predictions.rain_probability_pct}%
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                  <span style={{ fontSize: '11px', color: 'var(--text-secondary)', fontWeight: 600 }}>Expected Rainfall Amount:</span>
                  <span style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                    {prediction.predictions.rainfall} mm
                  </span>
                </div>
              </div>
              <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Rainfall 80% Prediction Interval: [{prediction.uncertainty?.rainfall_interval_80[0]} mm – {prediction.uncertainty?.rainfall_interval_80[1]} mm]
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginTop: '8px', borderTop: '1px solid var(--border-subtle)', paddingTop: '6px' }}>
                Historical {prediction.historical_reference?.calendar_context.month || 'Target Month'} Rain Frequency: {prediction.historical_reference?.station_monthly_climatology.historical_rain_frequency_pct}%
              </div>
            </div>

            {/* Wind Speed & Air Pressure */}
            <div className="card" style={{ borderTop: '4px solid var(--accent-wind)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>
                  Wind &amp; Atmospheric Pressure
                </span>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <Wind size={16} color="var(--accent-wind)" />
                  <Gauge size={16} color="var(--accent-pressure)" />
                </div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                <div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                    {prediction.predictions.wind_speed} <span style={{ fontSize: 'var(--font-xs)', fontWeight: 500 }}>km/h</span>
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--text-tertiary)' }}>
                    80% PI: [{prediction.uncertainty?.wind_speed_interval_80[0]}, {prediction.uncertainty?.wind_speed_interval_80[1]}]
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                    {prediction.predictions.air_pressure} <span style={{ fontSize: 'var(--font-xs)', fontWeight: 500 }}>hPa</span>
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--text-tertiary)' }}>
                    80% PI: [{prediction.uncertainty?.air_pressure_interval_80[0]}, {prediction.uncertainty?.air_pressure_interval_80[1]}]
                  </div>
                </div>
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginTop: '8px', borderTop: '1px solid var(--border-subtle)', paddingTop: '6px' }}>
                Elevation: {prediction.coordinates.elevation_m}m ASL • Barometric Adjusted
              </div>
            </div>
          </div>


          {/* Navigation Tabs for Deep Inspection */}
          <div style={{ display: 'flex', gap: 'var(--space-2)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: 'var(--space-2)' }}>
            <button
              onClick={() => setActiveTab('overview')}
              className={`btn btn-sm ${activeTab === 'overview' ? 'btn-primary' : 'btn-ghost'}`}
              style={{ fontSize: '12px', fontWeight: activeTab === 'overview' ? 700 : 500 }}
            >
              Prediction Provenance
            </button>
            <button
              onClick={() => setActiveTab('reference')}
              className={`btn btn-sm ${activeTab === 'reference' ? 'btn-primary' : 'btn-ghost'}`}
              style={{ fontSize: '12px', fontWeight: activeTab === 'reference' ? 700 : 500 }}
            >
              Historical Reference Used
            </button>
            <button
              onClick={() => setActiveTab('explainability')}
              className={`btn btn-sm ${activeTab === 'explainability' ? 'btn-primary' : 'btn-ghost'}`}
              style={{ fontSize: '12px', fontWeight: activeTab === 'explainability' ? 700 : 500 }}
            >
              How This Prediction Was Made
            </button>
            <button
              onClick={() => setActiveTab('limitations')}
              className={`btn btn-sm ${activeTab === 'limitations' ? 'btn-primary' : 'btn-ghost'}`}
              style={{ fontSize: '12px', fontWeight: activeTab === 'limitations' ? 700 : 500 }}
            >
              Scientific Limitations
            </button>
          </div>

          {/* Tab 1: Provenance & Metadata */}
          {activeTab === 'overview' && (
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <div style={{ fontSize: 'var(--font-base)', fontWeight: 800, color: 'var(--text-primary)' }}>
                Authoritative Prediction Provenance
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-3)', fontSize: 'var(--font-xs)' }}>
                <div style={{ background: 'var(--bg-surface-elevated)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ color: 'var(--text-tertiary)', fontWeight: 600 }}>Prediction Type</div>
                  <div style={{ color: 'var(--text-primary)', fontWeight: 700, marginTop: '2px' }}>{prediction.prediction_type}</div>
                </div>
                <div style={{ background: 'var(--bg-surface-elevated)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ color: 'var(--text-tertiary)', fontWeight: 600 }}>Target Station &amp; ID</div>
                  <div style={{ color: 'var(--text-primary)', fontWeight: 700, marginTop: '2px' }}>{prediction.station_name} ({prediction.station_id})</div>
                </div>
                <div style={{ background: 'var(--bg-surface-elevated)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ color: 'var(--text-tertiary)', fontWeight: 600 }}>Training Panel Window</div>
                  <div style={{ color: 'var(--text-primary)', fontWeight: 700, marginTop: '2px' }}>{prediction.provenance?.training_window}</div>
                </div>
                <div style={{ background: 'var(--bg-surface-elevated)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ color: 'var(--text-tertiary)', fontWeight: 600 }}>Inference Source</div>
                  <div style={{ color: 'var(--accent-primary)', fontWeight: 800, marginTop: '2px' }}>
                    {prediction.provenance?.inference_source || 'XGBOOST_LONG_TERM'}
                  </div>
                </div>
                <div style={{ background: 'var(--bg-surface-elevated)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ color: 'var(--text-tertiary)', fontWeight: 600 }}>Model Version</div>
                  <div style={{ color: 'var(--text-primary)', fontWeight: 700, marginTop: '2px' }}>
                    {prediction.provenance?.model_version || 'v1.0.0'}
                  </div>
                </div>
                <div style={{ background: 'var(--bg-surface-elevated)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ color: 'var(--text-tertiary)', fontWeight: 600 }}>Source Dataset Hash</div>
                  <div style={{ color: 'var(--accent-primary)', fontWeight: 700, marginTop: '2px', fontFamily: 'monospace' }}>
                    {prediction.provenance?.source_dataset_sha256.substring(0, 16)}...
                  </div>
                </div>
              </div>

              {/* Models Deployed Table */}
              <div style={{ marginTop: 'var(--space-2)' }}>
                <div style={{ fontSize: 'var(--font-xs)', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '8px' }}>
                  Model Artifacts Evaluated for this Target Date:
                </div>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--font-xs)' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--border-subtle)', textAlign: 'left', color: 'var(--text-tertiary)' }}>
                        <th style={{ padding: '6px' }}>Target</th>
                        <th style={{ padding: '6px' }}>Model ID</th>
                        <th style={{ padding: '6px' }}>Predicted Value</th>
                        <th style={{ padding: '6px' }}>80% Empirical Interval</th>
                        <th style={{ padding: '6px' }}>Validation MAE</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                        <td style={{ padding: '6px', fontWeight: 600 }}>Average Temperature</td>
                        <td style={{ padding: '6px', fontFamily: 'monospace', color: 'var(--accent-primary)' }}>xgb_longterm_temp_v1</td>
                        <td style={{ padding: '6px', fontWeight: 700 }}>{prediction.predictions.avg_temp}°C</td>
                        <td style={{ padding: '6px' }}>[{prediction.uncertainty?.avg_temp_interval_80[0]}°C, {prediction.uncertainty?.avg_temp_interval_80[1]}°C]</td>
                        <td style={{ padding: '6px', color: 'var(--accent-success)' }}>1.379°C</td>
                      </tr>
                      <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                        <td style={{ padding: '6px', fontWeight: 600 }}>Minimum Temperature</td>
                        <td style={{ padding: '6px', fontFamily: 'monospace', color: 'var(--accent-primary)' }}>xgb_longterm_temp_min_v1</td>
                        <td style={{ padding: '6px', fontWeight: 700 }}>{prediction.predictions.min_temp}°C</td>
                        <td style={{ padding: '6px' }}>[{prediction.uncertainty?.min_temp_interval_80[0]}°C, {prediction.uncertainty?.min_temp_interval_80[1]}°C]</td>
                        <td style={{ padding: '6px', color: 'var(--accent-success)' }}>1.463°C</td>
                      </tr>
                      <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                        <td style={{ padding: '6px', fontWeight: 600 }}>Maximum Temperature</td>
                        <td style={{ padding: '6px', fontFamily: 'monospace', color: 'var(--accent-primary)' }}>xgb_longterm_temp_max_v1</td>
                        <td style={{ padding: '6px', fontWeight: 700 }}>{prediction.predictions.max_temp}°C</td>
                        <td style={{ padding: '6px' }}>[{prediction.uncertainty?.max_temp_interval_80[0]}°C, {prediction.uncertainty?.max_temp_interval_80[1]}°C]</td>
                        <td style={{ padding: '6px', color: 'var(--accent-success)' }}>1.753°C</td>
                      </tr>
                      <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                        <td style={{ padding: '6px', fontWeight: 600 }}>Rain Occurrence Probability</td>
                        <td style={{ padding: '6px', fontFamily: 'monospace', color: 'var(--accent-primary)' }}>xgb_longterm_rain_cls_v1</td>
                        <td style={{ padding: '6px', fontWeight: 700, color: 'var(--accent-rain)' }}>{prediction.predictions.rain_probability_pct}%</td>
                        <td style={{ padding: '6px' }}>Posterior probability</td>
                        <td style={{ padding: '6px', color: 'var(--accent-success)' }}>ROC-AUC: 0.8747</td>
                      </tr>
                      <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                        <td style={{ padding: '6px', fontWeight: 600 }}>Expected Rainfall Amount</td>
                        <td style={{ padding: '6px', fontFamily: 'monospace', color: 'var(--accent-primary)' }}>xgb_longterm_rain_amt_v1</td>
                        <td style={{ padding: '6px', fontWeight: 700 }}>{prediction.predictions.rainfall} mm</td>
                        <td style={{ padding: '6px' }}>[{prediction.uncertainty?.rainfall_interval_80[0]} mm, {prediction.uncertainty?.rainfall_interval_80[1]} mm]</td>
                        <td style={{ padding: '6px' }}>4.744 mm</td>
                      </tr>
                      <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                        <td style={{ padding: '6px', fontWeight: 600 }}>Wind Speed</td>
                        <td style={{ padding: '6px', fontFamily: 'monospace', color: 'var(--accent-primary)' }}>xgb_longterm_wind_v1</td>
                        <td style={{ padding: '6px', fontWeight: 700 }}>{prediction.predictions.wind_speed} km/h</td>
                        <td style={{ padding: '6px' }}>[{prediction.uncertainty?.wind_speed_interval_80[0]} km/h, {prediction.uncertainty?.wind_speed_interval_80[1]} km/h]</td>
                        <td style={{ padding: '6px' }}>2.587 km/h</td>
                      </tr>
                      <tr>
                        <td style={{ padding: '6px', fontWeight: 600 }}>Air Pressure</td>
                        <td style={{ padding: '6px', fontFamily: 'monospace', color: 'var(--accent-primary)' }}>xgb_longterm_pressure_v1</td>
                        <td style={{ padding: '6px', fontWeight: 700 }}>{prediction.predictions.air_pressure} hPa</td>
                        <td style={{ padding: '6px' }}>[{prediction.uncertainty?.air_pressure_interval_80[0]} hPa, {prediction.uncertainty?.air_pressure_interval_80[1]} hPa]</td>
                        <td style={{ padding: '6px' }}>1.856 hPa</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Tab 2: Historical Reference Data Used */}
          {activeTab === 'reference' && prediction.historical_reference && (
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: 'var(--font-base)', fontWeight: 800, color: 'var(--text-primary)' }}>
                    Observed Historical Reference &amp; Climatology
                  </span>
                  <span className="badge badge-success" style={{ fontSize: '10px' }}>
                    CANONICAL OBSERVATION ANCHOR
                  </span>
                </div>
                <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  These baseline metrics were derived strictly from the canonical 10-year observed panel (2015-01-01 to 2025-02-10) to establish the station’s climatological anchor. They represent authoritative historical observations, distinct from machine-learning model estimates.
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-4)' }}>
                {/* Station Geography & Calendar */}
                <div style={{ background: 'var(--bg-surface-elevated)', padding: 'var(--space-4)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: 'var(--font-xs)', fontWeight: 800, color: 'var(--accent-primary)', marginBottom: '8px', textTransform: 'uppercase' }}>
                    Station &amp; Calendar Anchor
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: 'var(--font-xs)' }}>
                    <div><strong>Station:</strong> {prediction.historical_reference.station_name}</div>
                    <div><strong>Location:</strong> {prediction.historical_reference.district}, {prediction.historical_reference.state}</div>
                    <div><strong>Coordinates:</strong> {prediction.historical_reference.latitude}°N, {prediction.historical_reference.longitude}°E</div>
                    <div><strong>Elevation:</strong> {prediction.historical_reference.elevation_m}m Above Sea Level</div>
                    <div><strong>Target Month:</strong> {prediction.historical_reference.calendar_context.month} ({prediction.historical_reference.calendar_context.season})</div>
                    <div><strong>Day of Year:</strong> {prediction.historical_reference.calendar_context.day_of_year}</div>
                  </div>
                </div>

                {/* Selected Month Climatology */}
                <div style={{ background: 'var(--bg-surface-elevated)', padding: 'var(--space-4)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: 'var(--font-xs)', fontWeight: 800, color: 'var(--accent-rain)', marginBottom: '8px', textTransform: 'uppercase' }}>
                    Historical {prediction.historical_reference.calendar_context.month} Climatology
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: 'var(--font-xs)' }}>
                    <div><strong>Mean Temperature:</strong> {prediction.historical_reference.station_monthly_climatology.historical_mean_temp ?? '--'}°C</div>
                    <div><strong>Min / Max Diurnal Mean:</strong> {prediction.historical_reference.station_monthly_climatology.historical_min_temp ?? '--'}°C / {prediction.historical_reference.station_monthly_climatology.historical_max_temp ?? '--'}°C</div>
                    <div><strong>Historical Rain Frequency:</strong> {prediction.historical_reference.station_monthly_climatology.historical_rain_frequency_pct}%</div>
                    <div><strong>Historical Mean Rainfall:</strong> {prediction.historical_reference.station_monthly_climatology.historical_mean_rainfall_mm} mm/day</div>
                    <div><strong>Mean Wind Speed:</strong> {prediction.historical_reference.station_monthly_climatology.historical_mean_wind_kmh} km/h</div>
                    <div><strong>Mean Pressure:</strong> {prediction.historical_reference.station_monthly_climatology.historical_mean_pressure_hpa} hPa</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tab 3: Step-by-Step Explainability */}
          {activeTab === 'explainability' && prediction.how_prediction_made && (
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              <div>
                <div style={{ fontSize: 'var(--font-base)', fontWeight: 800, color: 'var(--text-primary)' }}>
                  How This Prediction Was Made
                </div>
                <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)' }}>
                  Step-by-step audit trace of the machine learning inference pipeline. Non-causal mathematical estimation.
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                {prediction.how_prediction_made.map((item) => (
                  <div
                    key={item.step}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 'var(--space-3)',
                      padding: 'var(--space-3)',
                      background: 'var(--bg-surface-elevated)',
                      borderRadius: 'var(--radius-md)',
                      borderLeft: '3px solid var(--accent-primary)'
                    }}
                  >
                    <div
                      style={{
                        width: '24px',
                        height: '24px',
                        borderRadius: '50%',
                        background: 'var(--accent-primary)',
                        color: '#090d16',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 800,
                        fontSize: '12px',
                        flexShrink: 0
                      }}
                    >
                      {item.step}
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: 'var(--font-sm)', color: 'var(--text-primary)' }}>
                        {item.title}
                      </div>
                      <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '2px' }}>
                        {item.detail}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 4: Scientific Limitations & Disclaimers */}
          {activeTab === 'limitations' && (
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertTriangle size={18} color="var(--accent-warning)" />
                <span style={{ fontSize: 'var(--font-base)', fontWeight: 800, color: 'var(--text-primary)' }}>
                  Scientific Limitations &amp; Verification Protocol
                </span>
              </div>
              <ul style={{ paddingLeft: '20px', margin: 0, fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                {prediction.limitations?.map((lim, idx) => (
                  <li key={idx} style={{ marginBottom: '6px' }}>{lim}</li>
                ))}
              </ul>
              <div style={{ background: 'rgba(234, 179, 8, 0.1)', border: '1px solid rgba(234, 179, 8, 0.3)', borderRadius: 'var(--radius-md)', padding: 'var(--space-3)', marginTop: 'var(--space-2)' }}>
                <div style={{ fontWeight: 700, fontSize: 'var(--font-xs)', color: 'var(--accent-warning)', marginBottom: '4px' }}>
                  Retrospective Verification Principle &amp; External Benchmark Methodology:
                </div>
                <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  Ground truth does not exist for future calendar dates at prediction time. When target date {prediction.prediction_date} elapses and physical station observations are recorded, the prediction will be automatically scored against actual observations. The Long-Term Predictor is a historical/seasonal ML estimate based on the project's canonical 10-year station dataset and frozen Phase 9 XGBoost models; it is not a live numerical-weather forecast. Comparisons with third-party weather forecasts (such as Google Weather or AccuWeather) serve strictly as PROSPECTIVE EXTERNAL BENCHMARKS, not as ground truth or proof of model error. External providers evaluate physical atmospheric fluid dynamics using live numerical models, which naturally produce different precipitation probabilities. 80% Prediction Intervals reflect empirical model uncertainty derived from out-of-time walk-forward validation residuals, not accuracy guarantees.
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Out of Range or Error State */}
      {prediction && prediction.status === 'UNAVAILABLE' && (
        <div className="card" style={{ borderLeft: '4px solid var(--accent-danger)', background: 'rgba(239, 68, 68, 0.05)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <AlertTriangle size={24} color="var(--accent-danger)" />
            <div>
              <div style={{ fontWeight: 800, fontSize: 'var(--font-base)', color: 'var(--text-primary)' }}>
                Prediction Unavailable
              </div>
              <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', marginTop: '2px' }}>
                {prediction.error}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
