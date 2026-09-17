# Phase 6 — Model Evaluation & Explainability Architecture

## Executive Architecture
Phase 6 establishes a scientific benchmarking and explainability engine for the **India Weather Forecasting & Intelligence System**. Operating across all Phase 3 forecasting models (Persistence/Majority Baselines, XGBoost, and PyTorch LSTM), the architecture executes comprehensive validation without altering any Phase 1–5 artifact or retraining any model.

```
+---------------------------------------------------------------------------------------+
|                    PHASE 6 EVALUATION & EXPLAINABILITY ENGINE                         |
+---------------------------------------------------------------------------------------+
                                           |
          +--------------------------------+--------------------------------+
          |                                |                                |
+----------------------+         +----------------------+         +---------------------+
| Baseline SHA-256 Lock|         | 18 Prediction        |         | 26 Features Matrix  |
| 41 Locked Artifacts  |         | Parquets (F1, F2, H) |         | features_engineered |
+----------------------+         +----------------------+         +---------------------+
          |                                |                                |
          +--------------------------------+--------------------------------+
                                           |
                                           v
                  [run_phase6_evaluation_engine.py]
                                           |
        +----------------------------------+----------------------------------+
        |                                  |                                  |
        v                                  v                                  v
[Multi-Target Benchmarks]      [Error Slices & Diagnostics]       [TreeSHAP Engine]
- Temperature (MAE, R2, RMSE)  - Elevation strata (5 tiers)       - Native pred_contribs
- Rainfall (overall/rainy MAE) - Rainfall intensity (IMD classes) - Global mean |SHAP|
- Rain Binary (Acc, AUC, Brier)- Threshold sweep (0.05 - 0.95)    - Local waterfalls
                               - Calibration ECE (10 bins)
        |                                  |                                  |
        +----------------------------------+----------------------------------+
                                           |
                                           v
               [phase6_evaluation_summary.json / authoritativeEvaluationSummary.json]
                                           |
        +----------------------------------+----------------------------------+
        |                                                                     |
        v                                                                     v
[Publication Plots (Task 26)]                         [Frontend UI Enhancement (Task 28)]
- feature_importance_shap_ranking.png                 - /models (TreeSHAP & Calibration tabs)
- reliability_calibration_diagram.png                 - Pure SVG SHAPFeatureImportanceChart
- threshold_tuning_curve.png                          - Pure SVG CalibrationDiagramChart
- elevation_error_distribution.png                    - Pure SVG ThresholdTuningChart
- model_benchmark_comparison_matrix.png
```

---

## Component Responsibilities

| Subsystem | Source Path | Architectural Guarantee |
| :--- | :--- | :--- |
| **Cryptographic Lock** | `phase6_evaluation/manifests/phase3_baseline_integrity_lock.json` | Bit-level SHA-256 validation across 41 Phase 3 files. |
| **Evaluation Engine** | `phase6_evaluation/scripts/run_phase6_evaluation_engine.py` | Multi-target benchmarking, error distribution, threshold sweep, and calibration curves. |
| **TreeSHAP Attributions** | `run_phase6_evaluation_engine.py` (via XGBoost `pred_contribs`) | Exact additive tree feature attributions with zero external dependency bloat. |
| **Visual Artifacts** | `phase6_evaluation/scripts/generate_phase6_plots.py` | Publication-quality 200 DPI evaluation charts in `phase6_evaluation/plots/`. |
| **Model Cards** | `phase6_model_cards.md` | Complete documentation of intended use, operating limits, and scientific uncertainties. |
| **Frontend Integration** | `frontend/src/pages/ModelsPage.tsx` + `frontend/src/components/charts/` | Interactive TreeSHAP and calibration diagnostics rendered with lightweight pure SVG. |
