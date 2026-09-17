import React from 'react';

interface ConfusionMatrixChartProps {
  title: string;
  matrix: number[][]; // [[TN, FP], [FN, TP]]
  modelName: string;
  splitName: string;
}

export const ConfusionMatrixChart: React.FC<ConfusionMatrixChartProps> = ({
  title,
  matrix,
  modelName,
  splitName
}) => {
  const tn = matrix[0]?.[0] ?? 0;
  const fp = matrix[0]?.[1] ?? 0;
  const fn = matrix[1]?.[0] ?? 0;
  const tp = matrix[1]?.[1] ?? 0;
  const total = tn + fp + fn + tp || 1;

  const precision = tp / (tp + fp) || 0;
  const recall = tp / (tp + fn) || 0;
  const accuracy = (tp + tn) / total || 0;
  const f1 = (2 * precision * recall) / (precision + recall) || 0;

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontSize: 'var(--font-sm)', fontWeight: 700, color: 'var(--text-primary)' }}>
            {title}
          </div>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)' }}>
            {modelName} • {splitName} (Total: {total.toLocaleString()} samples)
          </div>
        </div>
        <span className="badge badge-primary">Accuracy: {(accuracy * 100).toFixed(1)}%</span>
      </div>

      {/* 2x2 Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-2)' }}>
        {/* True Negative */}
        <div style={{
          background: 'color-mix(in srgb, var(--accent-success) 12%, var(--bg-surface-elevated))',
          border: '1px solid rgba(16, 185, 129, 0.25)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-3)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>
            True Dry (TN)
          </div>
          <div style={{ fontSize: 'var(--font-xl)', fontWeight: 800, color: 'var(--accent-success)', fontFamily: 'var(--font-mono)' }}>
            {tn.toLocaleString()}
          </div>
          <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-tertiary)' }}>
            {((tn / total) * 100).toFixed(1)}% of total
          </div>
        </div>

        {/* False Positive */}
        <div style={{
          background: 'color-mix(in srgb, var(--accent-danger) 10%, var(--bg-surface-elevated))',
          border: '1px solid rgba(239, 68, 68, 0.25)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-3)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>
            False Rain Alarm (FP)
          </div>
          <div style={{ fontSize: 'var(--font-xl)', fontWeight: 800, color: 'var(--accent-danger)', fontFamily: 'var(--font-mono)' }}>
            {fp.toLocaleString()}
          </div>
          <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-tertiary)' }}>
            {((fp / total) * 100).toFixed(1)}% of total
          </div>
        </div>

        {/* False Negative */}
        <div style={{
          background: 'color-mix(in srgb, var(--accent-warning) 10%, var(--bg-surface-elevated))',
          border: '1px solid rgba(245, 158, 11, 0.25)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-3)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>
            Missed Rain Event (FN)
          </div>
          <div style={{ fontSize: 'var(--font-xl)', fontWeight: 800, color: 'var(--accent-warning)', fontFamily: 'var(--font-mono)' }}>
            {fn.toLocaleString()}
          </div>
          <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-tertiary)' }}>
            {((fn / total) * 100).toFixed(1)}% of total
          </div>
        </div>

        {/* True Positive */}
        <div style={{
          background: 'color-mix(in srgb, var(--accent-primary) 14%, var(--bg-surface-elevated))',
          border: '1px solid rgba(56, 189, 248, 0.3)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-3)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>
            Detected Rain (TP)
          </div>
          <div style={{ fontSize: 'var(--font-xl)', fontWeight: 800, color: 'var(--accent-primary)', fontFamily: 'var(--font-mono)' }}>
            {tp.toLocaleString()}
          </div>
          <div style={{ fontSize: 'var(--font-2xs)', color: 'var(--text-tertiary)' }}>
            {((tp / total) * 100).toFixed(1)}% of total
          </div>
        </div>
      </div>

      {/* Sensitivity & Specificity Metrics */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid var(--border-subtle)', paddingTop: 'var(--space-3)', fontSize: 'var(--font-xs)' }}>
        <span style={{ color: 'var(--text-secondary)' }}>Precision: <b style={{ color: 'var(--text-primary)' }}>{(precision * 100).toFixed(1)}%</b></span>
        <span style={{ color: 'var(--text-secondary)' }}>Recall (TPR): <b style={{ color: 'var(--text-primary)' }}>{(recall * 100).toFixed(1)}%</b></span>
        <span style={{ color: 'var(--text-secondary)' }}>F1 Score: <b style={{ color: 'var(--accent-primary)' }}>{f1.toFixed(3)}</b></span>
      </div>
    </div>
  );
};
