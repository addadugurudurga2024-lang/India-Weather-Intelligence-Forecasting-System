import React, { useState } from 'react';
import { Award, Compass, Activity, Brain, CheckCircle2 } from 'lucide-react';
import {
  ModelComparisonBarChart,
  ConfusionMatrixChart,
  ROCCurveChart,
  SHAPFeatureImportanceChart,
  CalibrationDiagramChart,
  ThresholdTuningChart
} from '../components/charts';
import { metricsSummary } from '../data';
import evaluationSummary from '../data/authoritativeEvaluationSummary.json';

export const ModelsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'temperature' | 'rainfall' | 'classification' | 'explainability' | 'calibration'>('temperature');
  const [activeSplit, setActiveSplit] = useState<'holdout' | 'fold2' | 'fold1'>('holdout');

  const tempMetrics = metricsSummary.target_a_temperature;
  const rainMetrics = metricsSummary.target_b_rainfall_amount;

  const evalData = evaluationSummary as any;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Header & Production Decision Banner */}
      <div className="card" style={{
        background: 'linear-gradient(135deg, color-mix(in srgb, var(--accent-success) 12%, var(--bg-surface)) 0%, var(--bg-surface) 100%)',
        border: '1px solid var(--border-base)',
        padding: 'var(--space-6)'
      }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-4)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
            <div style={{
              width: '56px',
              height: '56px',
              borderRadius: 'var(--radius-lg)',
              background: 'var(--accent-success-subtle)',
              color: 'var(--accent-success)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Award size={32} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                <span style={{ fontSize: 'var(--font-xl)', fontWeight: 800, color: 'var(--text-primary)' }}>
                  Phase 6 Scientific Evaluation &amp; Benchmarking Ledger
                </span>
                <span className="badge badge-success">Audit Status: PASS</span>
              </div>
              <div style={{ fontSize: 'var(--font-sm)', color: 'var(--text-secondary)', marginTop: 'var(--space-1)' }}>
                Production Candidate: <b>XGBoost Tabular GBDT</b> (Evaluated alongside PyTorch LSTM Sequence Benchmark)
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
            <div className="badge badge-primary">SHA-256 Validated</div>
            <div className="badge badge-neutral">Native TreeSHAP</div>
            <div className="badge badge-warning">ECE: 6.08% Calibrated</div>
          </div>
        </div>

        {/* Scientific Nuance Callout */}
        <div style={{
          marginTop: 'var(--space-4)',
          borderTop: '1px solid var(--border-subtle)',
          paddingTop: 'var(--space-4)',
          fontSize: 'var(--font-xs)',
          color: 'var(--text-secondary)',
          lineHeight: 1.6
        }}>
          <b>Phase 6 Evidence Reassessment:</b> XGBoost remains the designated primary production candidate because it achieves superior validation stability, handles tabular lag and spatial features natively, delivers sub-millisecond inference (&lt;0.1ms/station), and provides native TreeSHAP transparency. PyTorch LSTM demonstrated genuine sequence representation strength on temperature holdout MAE (0.6441°C vs 0.6527°C) and rainy-day rainfall MAE (2.8630mm vs 2.8947mm). XGBoost is an evidence-based production candidate, not universally superior.
        </div>
      </div>

      {/* Target Selector Tabs & Split Toggle */}
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-4)' }}>
        {/* Target Tabs */}
        <div style={{ display: 'flex', gap: 'var(--space-2)', background: 'var(--bg-surface-elevated)', padding: '4px', borderRadius: 'var(--radius-lg)', flexWrap: 'wrap' }}>
          <button
            onClick={() => setActiveTab('temperature')}
            className={`btn btn-sm ${activeTab === 'temperature' ? 'btn-primary' : 'btn-ghost'}`}
          >
            Target A: Temperature
          </button>
          <button
            onClick={() => setActiveTab('rainfall')}
            className={`btn btn-sm ${activeTab === 'rainfall' ? 'btn-primary' : 'btn-ghost'}`}
          >
            Target B: Rainfall Amount
          </button>
          <button
            onClick={() => setActiveTab('classification')}
            className={`btn btn-sm ${activeTab === 'classification' ? 'btn-primary' : 'btn-ghost'}`}
          >
            Target C: Rain / No-Rain
          </button>
          <button
            onClick={() => setActiveTab('explainability')}
            className={`btn btn-sm ${activeTab === 'explainability' ? 'btn-primary' : 'btn-ghost'}`}
          >
            <Brain size={14} style={{ marginRight: '4px' }} />
            TreeSHAP Explainability
          </button>
          <button
            onClick={() => setActiveTab('calibration')}
            className={`btn btn-sm ${activeTab === 'calibration' ? 'btn-primary' : 'btn-ghost'}`}
          >
            <Activity size={14} style={{ marginRight: '4px' }} />
            Calibration &amp; Slices
          </button>
        </div>

        {/* Split Switcher (for benchmark tabs) */}
        {(activeTab === 'temperature' || activeTab === 'rainfall' || activeTab === 'classification') && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <span style={{ fontSize: 'var(--font-xs)', color: 'var(--text-tertiary)', fontWeight: 600 }}>Validation Split:</span>
            <div style={{ display: 'flex', gap: '4px', background: 'var(--bg-surface)', padding: '2px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-base)' }}>
              <button
                onClick={() => setActiveSplit('holdout')}
                className={`btn btn-sm ${activeSplit === 'holdout' ? 'btn-secondary' : 'btn-ghost'}`}
                style={{ fontWeight: activeSplit === 'holdout' ? 700 : 500 }}
              >
                2025 Holdout
              </button>
              <button
                onClick={() => setActiveSplit('fold2')}
                className={`btn btn-sm ${activeSplit === 'fold2' ? 'btn-secondary' : 'btn-ghost'}`}
                style={{ fontWeight: activeSplit === 'fold2' ? 700 : 500 }}
              >
                Fold 2 (2024)
              </button>
              <button
                onClick={() => setActiveSplit('fold1')}
                className={`btn btn-sm ${activeSplit === 'fold1' ? 'btn-secondary' : 'btn-ghost'}`}
                style={{ fontWeight: activeSplit === 'fold1' ? 700 : 500 }}
              >
                Fold 1 (2023)
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Target Content: Temperature */}
      {activeTab === 'temperature' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-4)' }}>
            <ModelComparisonBarChart
              title={`Temperature MAE (${activeSplit.toUpperCase()})`}
              metricLabel="Mean Absolute Error"
              unit="°C"
              lowerIsBetter={true}
              models={[
                {
                  name: 'Persistence Baseline',
                  value: activeSplit === 'holdout' ? (tempMetrics.baseline.holdout as any).mae : activeSplit === 'fold2' ? (tempMetrics.baseline.fold2_val as any).mae : (tempMetrics.baseline.fold1_val as any).mae,
                  color: 'var(--text-tertiary)'
                },
                {
                  name: 'XGBoost Tabular',
                  value: activeSplit === 'holdout' ? (tempMetrics.xgboost.holdout as any).mae : activeSplit === 'fold2' ? (tempMetrics.xgboost.fold2 as any).mae : (tempMetrics.xgboost.fold1 as any).mae,
                  color: 'var(--accent-primary)',
                  isPrimary: true
                },
                {
                  name: 'PyTorch LSTM',
                  value: activeSplit === 'holdout' ? (tempMetrics.lstm.holdout as any).mae : activeSplit === 'fold2' ? (tempMetrics.lstm.fold2 as any).mae : (tempMetrics.lstm.fold1 as any).mae,
                  color: 'var(--accent-purple)'
                }
              ]}
            />

            <ModelComparisonBarChart
              title={`Temperature R² Score (${activeSplit.toUpperCase()})`}
              metricLabel="Coefficient of Determination"
              unit=""
              lowerIsBetter={false}
              models={[
                {
                  name: 'Persistence Baseline',
                  value: activeSplit === 'holdout' ? (tempMetrics.baseline.holdout as any).r2 : activeSplit === 'fold2' ? (tempMetrics.baseline.fold2_val as any).r2 : (tempMetrics.baseline.fold1_val as any).r2,
                  color: 'var(--text-tertiary)'
                },
                {
                  name: 'XGBoost Tabular',
                  value: activeSplit === 'holdout' ? (tempMetrics.xgboost.holdout as any).r2 : activeSplit === 'fold2' ? (tempMetrics.xgboost.fold2 as any).r2 : (tempMetrics.xgboost.fold1 as any).r2,
                  color: 'var(--accent-primary)',
                  isPrimary: true
                },
                {
                  name: 'PyTorch LSTM',
                  value: activeSplit === 'holdout' ? (tempMetrics.lstm.holdout as any).r2 : activeSplit === 'fold2' ? (tempMetrics.lstm.fold2 as any).r2 : (tempMetrics.lstm.fold1 as any).r2,
                  color: 'var(--accent-purple)'
                }
              ]}
            />
          </div>

          {/* Full Metrics Table */}
          <div className="card" style={{ padding: 0 }}>
            <div style={{ padding: 'var(--space-4) var(--space-5)', borderBottom: '1px solid var(--border-subtle)' }}>
              <div style={{ fontWeight: 700, fontSize: 'var(--font-base)', color: 'var(--text-primary)' }}>
                Temperature Regression Metric Ledger (Authoritative Phase 3 Results)
              </div>
            </div>
            <div className="data-table-container" style={{ border: 'none' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Model Family</th>
                    <th>Fold 1 Val MAE</th>
                    <th>Fold 1 Val R²</th>
                    <th>Fold 2 Val MAE</th>
                    <th>Fold 2 Val R²</th>
                    <th>2025 Holdout MAE</th>
                    <th>2025 Holdout R²</th>
                    <th>Inference Speed</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><b>Persistence Baseline</b></td>
                    <td>0.7298°C</td>
                    <td>0.9582</td>
                    <td>0.7185°C</td>
                    <td>0.9660</td>
                    <td>0.7235°C</td>
                    <td>0.9635</td>
                    <td>&lt;0.01 ms</td>
                  </tr>
                  <tr style={{ background: 'var(--accent-primary-subtle)' }}>
                    <td><b style={{ color: 'var(--accent-primary)' }}>XGBoost (Production Candidate)</b></td>
                    <td><b>0.7161°C</b></td>
                    <td><b>0.9621</b></td>
                    <td><b>0.7015°C</b></td>
                    <td><b>0.9693</b></td>
                    <td><b>0.6527°C</b></td>
                    <td><b>0.9705</b></td>
                    <td><b>&lt;0.10 ms</b></td>
                  </tr>
                  <tr>
                    <td><b>PyTorch LSTM (7-Day Sequence)</b></td>
                    <td>0.7854°C</td>
                    <td>0.9568</td>
                    <td>0.7115°C</td>
                    <td>0.9673</td>
                    <td><b style={{ color: 'var(--accent-purple)' }}>0.6441°C</b></td>
                    <td><b style={{ color: 'var(--accent-purple)' }}>0.9713</b></td>
                    <td>~1.20 ms</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Target Content: Rainfall */}
      {activeTab === 'rainfall' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-4)' }}>
            <ModelComparisonBarChart
              title={`Rainfall Amount MAE (${activeSplit.toUpperCase()})`}
              metricLabel="Mean Absolute Error across all valid records"
              unit="mm"
              lowerIsBetter={true}
              models={[
                {
                  name: 'Persistence Baseline',
                  value: activeSplit === 'holdout' ? (rainMetrics.baseline.holdout as any).mae : activeSplit === 'fold2' ? (rainMetrics.baseline.fold2_val as any).mae : (rainMetrics.baseline.fold1_val as any).mae,
                  color: 'var(--text-tertiary)'
                },
                {
                  name: 'XGBoost Tabular (log1p)',
                  value: activeSplit === 'holdout' ? (rainMetrics.xgboost.holdout as any).mae : activeSplit === 'fold2' ? (rainMetrics.xgboost.fold2 as any).mae : (rainMetrics.xgboost.fold1 as any).mae,
                  color: 'var(--accent-primary)',
                  isPrimary: true
                },
                {
                  name: 'PyTorch LSTM (log1p)',
                  value: activeSplit === 'holdout' ? (rainMetrics.lstm.holdout as any).mae : activeSplit === 'fold2' ? (rainMetrics.lstm.fold2 as any).mae : (rainMetrics.lstm.fold1 as any).mae,
                  color: 'var(--accent-purple)'
                }
              ]}
            />

            <ModelComparisonBarChart
              title={`Rainy-Days Only MAE (${activeSplit.toUpperCase()})`}
              metricLabel="MAE on observations with Rain > 0mm"
              unit="mm"
              lowerIsBetter={true}
              models={[
                {
                  name: 'Persistence Baseline',
                  value: activeSplit === 'holdout' ? 3.4563 : activeSplit === 'fold2' ? 8.6904 : 7.7535,
                  color: 'var(--text-tertiary)'
                },
                {
                  name: 'XGBoost Tabular (log1p)',
                  value: activeSplit === 'holdout' ? 2.8947 : activeSplit === 'fold2' ? 7.1290 : 6.4920,
                  color: 'var(--accent-primary)',
                  isPrimary: true
                },
                {
                  name: 'PyTorch LSTM (log1p)',
                  value: activeSplit === 'holdout' ? 2.8630 : activeSplit === 'fold2' ? 7.0867 : 6.5533,
                  color: 'var(--accent-purple)'
                }
              ]}
            />
          </div>

          {/* Full Rainfall Metrics Table */}
          <div className="card" style={{ padding: 0 }}>
            <div style={{ padding: 'var(--space-4) var(--space-5)', borderBottom: '1px solid var(--border-subtle)' }}>
              <div style={{ fontWeight: 700, fontSize: 'var(--font-base)', color: 'var(--text-primary)' }}>
                Rainfall Amount Regression Metric Ledger (log1p Transformed)
              </div>
            </div>
            <div className="data-table-container" style={{ border: 'none' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Model Family</th>
                    <th>Fold 1 Val MAE</th>
                    <th>Fold 2 Val MAE</th>
                    <th>Fold 2 Val R²</th>
                    <th>Fold 2 Rainy MAE</th>
                    <th>2025 Holdout MAE</th>
                    <th>Holdout Rainy MAE</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><b>Persistence Baseline</b></td>
                    <td>3.7251 mm</td>
                    <td>4.2735 mm</td>
                    <td>0.0157</td>
                    <td>8.6904 mm</td>
                    <td>0.5026 mm</td>
                    <td>3.4563 mm</td>
                  </tr>
                  <tr style={{ background: 'var(--accent-primary-subtle)' }}>
                    <td><b style={{ color: 'var(--accent-primary)' }}>XGBoost (Production Candidate)</b></td>
                    <td><b>3.0110 mm</b></td>
                    <td><b>3.3739 mm</b></td>
                    <td>0.2844</td>
                    <td>7.1290 mm</td>
                    <td><b>0.4344 mm</b></td>
                    <td>2.8947 mm</td>
                  </tr>
                  <tr>
                    <td><b>PyTorch LSTM (7-Day Sequence)</b></td>
                    <td>3.0686 mm</td>
                    <td>3.3873 mm</td>
                    <td><b style={{ color: 'var(--accent-purple)' }}>0.3165</b></td>
                    <td><b style={{ color: 'var(--accent-purple)' }}>7.0867 mm</b></td>
                    <td>0.4368 mm</td>
                    <td><b style={{ color: 'var(--accent-purple)' }}>2.8630 mm</b></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Target Content: Classification */}
      {activeTab === 'classification' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-4)' }}>
            <ConfusionMatrixChart
              title="XGBoost Confusion Matrix"
              matrix={[[13884, 740], [1025, 674]]}
              modelName="XGBoost Classifier"
              splitName="2025 Holdout"
            />
            <ROCCurveChart
              title="ROC Discrimination Curve"
              auc={activeSplit === 'holdout' ? 0.8366 : 0.9193}
              modelName="XGBoost Classifier"
              splitName={activeSplit === 'holdout' ? 'Holdout 2025' : 'Fold 2 Val'}
            />
          </div>

          {/* Classification Metrics Table */}
          <div className="card" style={{ padding: 0 }}>
            <div style={{ padding: 'var(--space-4) var(--space-5)', borderBottom: '1px solid var(--border-subtle)' }}>
              <div style={{ fontWeight: 700, fontSize: 'var(--font-base)', color: 'var(--text-primary)' }}>
                Rain / No-Rain Classification Ledger
              </div>
            </div>
            <div className="data-table-container" style={{ border: 'none' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Model Family</th>
                    <th>Fold 2 Val Acc</th>
                    <th>Fold 2 Val F1</th>
                    <th>Fold 2 ROC-AUC</th>
                    <th>Fold 2 PR-AUC</th>
                    <th>2025 Holdout Acc</th>
                    <th>Holdout ROC-AUC</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><b>Majority Baseline (Dry)</b></td>
                    <td>55.78%</td>
                    <td>0.0000</td>
                    <td>0.5000</td>
                    <td>0.4422</td>
                    <td>89.59%</td>
                    <td>0.5000</td>
                  </tr>
                  <tr style={{ background: 'var(--accent-primary-subtle)' }}>
                    <td><b style={{ color: 'var(--accent-primary)' }}>XGBoost (Production Candidate)</b></td>
                    <td><b>84.76%</b></td>
                    <td><b>0.8300</b></td>
                    <td><b>0.9193</b></td>
                    <td><b>0.9076</b></td>
                    <td><b>89.19%</b></td>
                    <td><b>0.8366</b></td>
                  </tr>
                  <tr>
                    <td><b>PyTorch LSTM (7-Day Sequence)</b></td>
                    <td>83.76%</td>
                    <td>0.8197</td>
                    <td>0.9096</td>
                    <td>0.8994</td>
                    <td>88.32%</td>
                    <td>0.8256</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Target Content: TreeSHAP Explainability */}
      {activeTab === 'explainability' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: 'var(--space-4)' }}>
            <SHAPFeatureImportanceChart
              title="Temperature Regressor SHAP Rankings"
              subtitle="Mean absolute SHAP impact (°C) across 26 engineered features"
              features={evalData.explainability.temperature_shap_rankings}
              unitLabel="°C"
              primaryColor="var(--accent-primary)"
            />
            <SHAPFeatureImportanceChart
              title="Rain Classifier SHAP Rankings"
              subtitle="Mean absolute SHAP impact on log-odds of rain probability"
              features={evalData.explainability.rain_classification_shap_rankings}
              unitLabel="log-odds"
              primaryColor="var(--accent-success)"
            />
          </div>

          {/* Local Prediction Case Studies */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            <div style={{ fontSize: 'var(--font-base)', fontWeight: 800, color: 'var(--text-primary)' }}>
              Representative Local Prediction Attributions (TreeSHAP Waterfall)
            </div>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-secondary)' }}>
              Local breakdowns demonstrating how individual station observations shift model predictions relative to base expectation.
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-3)', marginTop: 'var(--space-2)' }}>
              {evalData.explainability.local_case_studies.filter(Boolean).map((cs: any, i: number) => (
                <div key={i} style={{
                  background: 'var(--bg-surface-elevated)',
                  padding: 'var(--space-3)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                  fontSize: 'var(--font-xs)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <b style={{ color: 'var(--accent-primary)' }}>{cs.scenario}</b>
                    <span className="badge badge-neutral" style={{ fontSize: '10px' }}>{cs.date}</span>
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                    Station: {cs.station} ({cs.state}) {cs.elevation ? `— ${cs.elevation}m` : ''}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border-subtle)', paddingTop: '4px', marginTop: '2px' }}>
                    <span>Base Value: <b>{cs.base_value}°C</b></span>
                    <span>Predicted: <b style={{ color: 'var(--text-primary)' }}>{cs.predicted_temp}°C</b></span>
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', marginTop: '2px' }}>Top Contributors:</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                    {cs.top_contributions.map((c: any) => (
                      <div key={c.feature} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px' }}>
                        <code>{c.feature} = {c.value}</code>
                        <span style={{ color: c.shap_impact > 0 ? 'var(--accent-danger)' : 'var(--accent-primary)', fontWeight: 700 }}>
                          {c.shap_impact > 0 ? `+${c.shap_impact}` : c.shap_impact}°C
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Target Content: Calibration & Error Slices */}
      {activeTab === 'calibration' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: 'var(--space-4)' }}>
            <CalibrationDiagramChart
              title="Rain Probability Reliability Diagram"
              bins={evalData.calibration.reliability_bins}
              ece={evalData.calibration.expected_calibration_error}
              brierScore={evalData.calibration.brier_score}
            />
            <ThresholdTuningChart
              title="Classification Threshold Sweep (0.05 – 0.95)"
              sweep={evalData.threshold_analysis.sweep}
              optimalThreshold={evalData.threshold_analysis.optimal_f1_threshold}
              defaultThreshold={0.50}
            />
          </div>

          {/* Elevation Error Slices Table */}
          <div className="card" style={{ padding: 0 }}>
            <div style={{ padding: 'var(--space-4) var(--space-5)', borderBottom: '1px solid var(--border-subtle)' }}>
              <div style={{ fontWeight: 700, fontSize: 'var(--font-base)', color: 'var(--text-primary)' }}>
                Temperature Forecast Error Stratified by Topographic Elevation Band
              </div>
            </div>
            <div className="data-table-container" style={{ border: 'none' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Elevation Band</th>
                    <th>Sample Station-Days</th>
                    <th>Mean Absolute Error (MAE)</th>
                    <th>Median Error</th>
                  </tr>
                </thead>
                <tbody>
                  {evalData.error_slices.elevation_slices.map((slice: any) => (
                    <tr key={slice.band}>
                      <td><b>{slice.band}</b></td>
                      <td>{slice.count.toLocaleString()}</td>
                      <td style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>{slice.mae}°C</td>
                      <td>{slice.median_error}°C</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Strongest vs Weakest Stations */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-4)' }}>
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              <div style={{ fontWeight: 700, fontSize: 'var(--font-sm)', color: 'var(--accent-success)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <CheckCircle2 size={16} /> Top 5 Strongest Performing Stations (N ≥ 30)
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: 'var(--font-xs)', marginTop: '4px' }}>
                {evalData.error_slices.station_extremes.strongest_stations.map((stn: any) => (
                  <div key={stn.station_id} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                    <span>{stn.station_name} ({stn.state})</span>
                    <b style={{ color: 'var(--accent-success)' }}>{stn.mae}°C MAE</b>
                  </div>
                ))}
              </div>
            </div>

            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              <div style={{ fontWeight: 700, fontSize: 'var(--font-sm)', color: 'var(--accent-warning)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Compass size={16} /> Top 5 Challenging Stations (High Mountain / Microclimates)
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: 'var(--font-xs)', marginTop: '4px' }}>
                {evalData.error_slices.station_extremes.weakest_stations.map((stn: any) => (
                  <div key={stn.station_id} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                    <span>{stn.station_name} ({stn.state}) — {stn.elevation_m}m</span>
                    <b style={{ color: 'var(--accent-warning)' }}>{stn.mae}°C MAE</b>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
