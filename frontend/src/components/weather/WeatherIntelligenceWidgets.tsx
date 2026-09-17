import React from 'react';
import { AlertTriangle, Info, Zap } from 'lucide-react';

interface RainRiskWidgetProps {
  probability: number; // 0 to 1
  predictedAmountMm?: number;
}

export const RainRiskWidget: React.FC<RainRiskWidgetProps> = ({ probability, predictedAmountMm = 0 }) => {
  let riskLevel = 'LOW';
  let badgeClass = 'badge-success';
  let desc = 'Minimal precipitation expected across the district.';

  if (probability >= 0.7 || predictedAmountMm > 25) {
    riskLevel = 'HIGH';
    badgeClass = 'badge-danger';
    desc = 'Substantial convective or monsoon precipitation indicated.';
  } else if (probability >= 0.4 || predictedAmountMm > 5) {
    riskLevel = 'MODERATE';
    badgeClass = 'badge-warning';
    desc = 'Scattered showers or drizzle possible in local pockets.';
  }

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Zap size={16} style={{ color: 'var(--accent-rain)' }} />
          <span style={{ fontSize: 'var(--font-sm)', fontWeight: 700, color: 'var(--text-primary)' }}>
            Precipitation Risk Assessment
          </span>
        </div>
        <span className={`badge ${badgeClass}`}>{riskLevel} RISK</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: 'var(--space-2)' }}>
        <span style={{ fontSize: 'var(--font-3xl)', fontWeight: 800, color: 'var(--accent-rain)', fontFamily: 'var(--font-mono)' }}>
          {Math.round(probability * 100)}%
        </span>
        <span style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)' }}>
          Predicted Probability • Expected Vol: <b>{predictedAmountMm} mm</b>
        </span>
      </div>

      <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)', borderTop: '1px solid var(--border-subtle)', paddingTop: 'var(--space-2)' }}>
        {desc}
      </div>
    </div>
  );
};

export const WeatherAlertWidget: React.FC<{ stationName: string; tempC: number; rainMm: number }> = ({
  stationName,
  tempC,
  rainMm
}) => {
  const alerts: { title: string; severity: 'warning' | 'info'; text: string }[] = [];

  if (tempC < 6.0) {
    alerts.push({
      title: 'Ground Frost & Cold Wave Watch',
      severity: 'warning',
      text: `Surface temperature observed at ${tempC}°C in ${stationName}. Diurnal freeze potential.`
    });
  } else if (tempC > 40.0) {
    alerts.push({
      title: 'High Heat Index Advisory',
      severity: 'warning',
      text: `Extreme temperature recorded at ${tempC}°C. High dehydration risk.`
    });
  }

  if (rainMm > 50.0) {
    alerts.push({
      title: 'Heavy Rainfall Warning',
      severity: 'warning',
      text: `Recorded 24h accumulation reached ${rainMm}mm. Localized waterlogging possible.`
    });
  }

  if (alerts.length === 0) {
    alerts.push({
      title: 'Nominal Weather Conditions',
      severity: 'info',
      text: `No active meteorological severity advisories for ${stationName}. Observations conform to climatological norms.`
    });
  }

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
        <AlertTriangle size={18} style={{ color: alerts[0].severity === 'warning' ? 'var(--accent-warning)' : 'var(--accent-success)' }} />
        <span style={{ fontSize: 'var(--font-sm)', fontWeight: 700, color: 'var(--text-primary)' }}>
          Meteorological Advisory Feed
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        {alerts.map((a, idx) => (
          <div
            key={idx}
            style={{
              padding: 'var(--space-3)',
              borderRadius: 'var(--radius-md)',
              background: a.severity === 'warning' ? 'color-mix(in srgb, var(--accent-warning) 10%, var(--bg-surface-elevated))' : 'var(--bg-surface-elevated)',
              border: `1px solid ${a.severity === 'warning' ? 'rgba(245, 158, 11, 0.3)' : 'var(--border-subtle)'}`
            }}
          >
            <div style={{ fontWeight: 700, fontSize: 'var(--font-xs)', color: 'var(--text-primary)' }}>{a.title}</div>
            <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-secondary)', marginTop: '2px' }}>{a.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const ModelExplanationWidget: React.FC<{ modelName: string }> = ({ modelName }) => {
  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Info size={16} style={{ color: 'var(--accent-primary)' }} />
          <span style={{ fontSize: 'var(--font-sm)', fontWeight: 700, color: 'var(--text-primary)' }}>
            Model Inference Transparency
          </span>
        </div>
        <span className="badge badge-neutral">{modelName}</span>
      </div>

      <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
        Inference employs 26 backward-looking features. Primary model feature weights are led by:
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', fontSize: 'var(--font-xs)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>1. Prior-day Average Temperature (<code style={{ fontFamily: 'var(--font-mono)' }}>lag_1_avg_temp</code>)</span>
          <b style={{ color: 'var(--accent-temp)' }}>42.8% Importance</b>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>2. 3-Day Rolling Mean (<code style={{ fontFamily: 'var(--font-mono)' }}>rolling_3d_temp_mean</code>)</span>
          <b style={{ color: 'var(--accent-temp)' }}>19.4% Importance</b>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>3. Surface Barometric Pressure (<code style={{ fontFamily: 'var(--font-mono)' }}>air_pressure</code>)</span>
          <b style={{ color: 'var(--accent-primary)' }}>11.2% Importance</b>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>4. Elevation &amp; Latitude (<code style={{ fontFamily: 'var(--font-mono)' }}>elevation, latitude</code>)</span>
          <b style={{ color: 'var(--accent-purple)' }}>8.7% Importance</b>
        </div>
      </div>
    </div>
  );
};
