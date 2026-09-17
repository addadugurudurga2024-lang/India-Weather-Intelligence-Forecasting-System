# Phase 7 — Full Repository Reconnaissance Report

**Project**: India Weather Forecasting & Intelligence System  
**Phase**: PHASE 7 — Operational 25-Day Weather Timeline + 12-Day Multi-Horizon Forecasting  
**Authoritative Date**: 2026-09-13  
**Status**: AUDIT COMPLETE — RECONNAISSANCE LOCKED  

---

## 1. Executive Summary & Objective

Phase 7 expands the India Weather Forecasting & Intelligence System from a next-day point forecast ($t+1$) into an operational 25-day weather intelligence system:
$$\underbrace{D-12 \to D-11 \to \dots \to D-1}_{\text{12 Days Actual Recorded Observations}} \quad\longrightarrow\quad \underbrace{D0}_{\text{Today / Current Observed Conditions}} \quad\longrightarrow\quad \underbrace{D+1 \to D+2 \to \dots \to D+12}_{\text{12 Days Multi-Horizon Model Forecasts}}$$

This reconnaissance establishes the exact foundation across the codebase, datasets, models, evaluation metrics, and frontend architecture, ensuring zero fabrication, strict data provenance, immutable raw data preservation, and rigorous temporal leakage prevention.

---

## 2. Comprehensive Inventory of Existing Assets

### 2.1 Raw Data & Phase 1 Integrity
- **Raw Kaggle Source**: `D:\Downloads\india_weather_rainfall_data.xlsx` (64,579,550 bytes)
- **Cryptographic SHA-256**: `e6a636777430f078b4d970f9f46e79efcece7f97b67dd186c30a755d2783cd84`
- **Cached Read-Only Copy**: `phase1_audit/cache/india_weather_rainfall_data_cached.parquet` (6,856,200 bytes)
- **Status**: **STRICTLY IMMUTABLE**. The file has not been altered, overwritten, or modified in place.

### 2.2 Phase 2 Canonical Datasets & Features
Located in `phase2_canonical/outputs/`:
1. `canonical_weather_full.parquet`: Complete dataset (968,849 rows).
2. `canonical_weather_forecasting.parquet`: Audited modern panel (604,155 daily records, 2021-01-01 to 2025-02-10).
3. `features_engineered.parquet`: 604,155 rows $\times$ 40 columns (26 model input features + metadata + next-day targets).
4. `station_metadata.json`: 413 physical stations mapped to `{slug}_{lat:.4f}_{lon:.4f}_{elev}m` primary keys.
5. `data_dictionary.json`: Schema documentation across all clean and raw fields.
6. `temporal_split_manifest.json`:
   - **Fold 1**: Train 2021-01-01 to 2022-12-31 (290,531 rows), Val 2023-01-01 to 2023-12-31 (149,423 rows).
   - **Fold 2**: Train 2021-01-01 to 2023-12-31 (439,954 rows), Val 2024-01-01 to 2024-12-31 (147,469 rows).
   - **Holdout**: 2025-01-01 to 2025-02-10 (16,732 rows).

### 2.3 Phase 3 Model Artifacts
All 41 baseline artifacts are locked under cryptographic SHA-256 in `phase6_evaluation/manifests/phase3_baseline_integrity_lock.json`:
- **XGBoost Models**:
  - `phase3_models/xgboost/temperature/xgb_temp_fold2.json`
  - `phase3_models/xgboost/rainfall/xgb_rain_amt_fold2.json`
  - `phase3_models/xgboost/rain_classification/xgb_rain_cls_fold2.json`
- **PyTorch LSTM Models**:
  - `phase3_models/lstm/temperature/lstm_temperature_fold2.pt`
  - `phase3_models/lstm/rainfall/lstm_rainfall_fold2.pt`
  - `phase3_models/lstm/rain_classification/lstm_rain_classification_fold2.pt`
- **Preprocessors**: StandardScalers in `phase3_models/preprocessors/`
- **Predictions**: 18 parquet files in `phase3_models/predictions/` across 3 folds $\times$ 2 models $\times$ 3 targets.

### 2.4 Authoritative Benchmark Metrics (Phases 3 & 6 Reconciled)
From `frontend/src/data/authoritativeMetrics.json` and `phase6_evaluation/data/phase6_evaluation_summary.json`:
- **Target A — Temperature (Holdout 2025)**:
  - Persistence Baseline: MAE $0.7235^\circ\text{C}$
  - XGBoost (Production Candidate): MAE $0.6527^\circ\text{C}$, RMSE $0.9328^\circ\text{C}$, $R^2 = 0.9785$
  - LSTM: MAE $0.6441^\circ\text{C}$, RMSE $0.9234^\circ\text{C}$, $R^2 = 0.9789$
- **Target B — Rainfall Amount (Holdout 2025)**:
  - Persistence Baseline: MAE $0.5186\text{ mm}$ (Rainy-day MAE $3.4563\text{ mm}$)
  - XGBoost (Production Candidate): MAE $0.4344\text{ mm}$, RMSE $2.2030\text{ mm}$ (Rainy-day MAE $2.8947\text{ mm}$)
  - LSTM: MAE $0.4368\text{ mm}$, RMSE $2.2057\text{ mm}$ (Rainy-day MAE $2.8630\text{ mm}$)
- **Target C — Rain Binary Classification (Holdout 2025)**:
  - Majority Class Baseline: Accuracy $89.59\%$
  - XGBoost: Accuracy $89.19\%$, ROC-AUC $0.8366$, PR-AUC $0.4493$ (at $\tau=0.30$)
  - LSTM: Accuracy $88.32\%$, ROC-AUC $0.8256$

### 2.5 Frontend Architecture & Current Forecast Center
Located in `frontend/`:
- **Vite + React 18 + TypeScript** with custom CSS design tokens (`frontend/src/index.css`).
- **Active Route**: `/forecast` rendered by `frontend/src/pages/ForecastPage.tsx`.
- **Current Forecast Service**: `frontend/src/services/forecastService.ts` currently serves static snapshot data (`mockForecastResults` and `authoritativeForecastSnapshots.json`).
- **Data Schemas**: `frontend/src/types/index.ts` specifies `ForecastResult`, `WeatherObservation`, `Station`, `MetricsSummary`.
- **Widgets**: `RainRiskWidget`, `WeatherAlertWidget`, `ModelExplanationWidget` in `frontend/src/components/weather/WeatherIntelligenceWidgets.tsx`.
- **Geographic System**: Leaflet + pure SVG map components in `frontend/src/pages/MapPage.tsx` and `frontend/src/components/maps/`.

### 2.6 MongoDB Schemas & Database Infrastructure
Located in `phase4_database/`:
- `forecast_results.schema.json`: Strict JSON schema with BSON validation.
- `weather_observations.schema.json`: Validation schema for daily station observations.
- `model_metadata.schema.json`: Model configuration registry.
- `stations.schema.json`: 413 station registry with geospatial 2dsphere indexing.
- `seed_development_db.py`: Deterministic seed execution engine.

### 2.7 Testing & Verification Infrastructure
Located in `tests/`:
- `test_phase4_frontend_and_database.py`: 5 passing tests.
- `test_phase5_maps_and_geospatial.py`: 7 passing tests.
- `test_phase6_evaluation_and_explainability.py`: 5 passing tests.
- Static checking: `oxlint` (0 errors), `tsc -b` (0 errors), `vite build` (0 errors).

---

## 3. Critical Constraints & Operational Boundary Audit

| Boundary Dimension | State / Rule | Rationale |
| :--- | :--- | :--- |
| **Historical Dataset Limit** | Ends on **2025-02-10** | Any operational date past 2025-02-10 (e.g. 2026-09-13) cannot use Kaggle historical data for $D-12 \dots D0$. |
| **Data Fabrication** | **STRICTLY ZERO** | If data is unavailable, return `null` and status `"UNAVAILABLE"`. Never fill with arbitrary averages or fake values. |
| **Humidity Variable** | **OUT OF SCOPE** | Not in canonical Kaggle dataset; must NOT be incorporated into core models. |
| **Hourly Weather** | **OUT OF SCOPE** | Daily aggregated data cannot support "rain starts at 4:20 PM" or hourly temperatures. |
| **Data Provenance** | **MANDATORY** | Every value must declare: `OBSERVED`, `CURRENT`, `FORECAST`, `DERIVED`, or `UNAVAILABLE`. |
| **Phase Boundaries** | **NO PHASE 8** | No conversational AI, LLM chatbots, or FastAPI backend deployments. |

---

## 4. Operational Ingestion & Data Source Feasibility Audit (Task 20 Preview)

1. **IMD AWS (Indian Meteorological Department)**:
   - IMD operates public AWS data portals (`mausam.imd.gov.in`), but lacks a stable, authenticated, machine-readable JSON API for bulk multi-year station queries without session scraping.
2. **Open-Meteo Historical Archive & Forecast API**:
   - Evaluated endpoint: `https://api.open-meteo.com/v1/forecast` and `https://archive-api.open-meteo.com/v1/archive`.
   - **Licensing**: Open Database License / Creative Commons Attribution 4.0 (CC BY 4.0), non-commercial open access.
   - **Station Coverage**: Exact GPS coordinate interpolation (latitude/longitude) matching all 413 canonical stations.
   - **Supported Variables**: Daily mean temperature (`temperature_2m_mean`), max (`temperature_2m_max`), min (`temperature_2m_min`), wind speed (`wind_speed_10m_max`), surface pressure (`surface_pressure`), rainfall sum (`precipitation_sum`).
   - **Reliability & Availability**: HTTP 200 validated during reconnaissance with $<50\text{ ms}$ latency.
   - **Fallback Policy**: When offline, unconfigured, or failing, the system renders explicit `"CURRENT DATA UNAVAILABLE"` without synthetic imputation.

---

## 5. Architectural Gap Analysis for Phase 7

1. **Multi-Horizon Modeling Gap**:
   - Current Phase 3 models only predict $t+1$. We must engineer multi-horizon targets ($T+1 \dots T+12$) for all 5 target variables (avg temp, min temp, max temp, wind speed, air pressure, rainfall amount, rain occurrence).
2. **Horizon-Specific Error Degradation**:
   - Forecast skill inevitably degrades as horizon increases from 24 hours to 288 hours ($T+12$). We must compute exact MAE/RMSE/$R^2$ degradation curves to scientifically prove at which horizon skill decays toward climatology.
3. **Uncertainty Quantification Gap**:
   - Phase 3 provided single-point predictions. Phase 7 requires empirical quantile residual intervals (e.g. 80% and 95% prediction intervals) for continuous forecasts and calibrated probabilities for rain occurrence.
4. **25-Day Unified Result Contract**:
   - Frontend and schemas need a unified 25-day timeline contract displaying:
     - 12 days actual measured observations ($D-12 \dots D-1$)
     - 1 current observed day ($D0$)
     - 12 days model forecasts ($D+1 \dots D+12$)
     - Distinct visual styling, status badges, and uncertainty bands.

---

## 6. Conclusion

The repository is clean, verified, and ready for Phase 7 execution. All 41 Phase 3 baseline artifacts and Phase 6 evaluation suites remain cryptographically protected and unchanged.
