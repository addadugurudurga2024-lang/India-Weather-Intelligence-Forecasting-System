# Phase 7 — Post-Completion Forecast Audit & Pipeline Reconnaissance

**Project**: India Weather Forecasting & Intelligence System  
**Document**: Phase 7 Post-Audit Baseline Reconnaissance (Task 1)  
**Authoritative Date**: 2026-09-13  
**Status**: AUDIT RECONNAISSANCE COMPLETE  

---

## 1. Inventory of Phase 7 Operational & Modeling Assets

### 1.1 Source Code & Execution Paths
- **Master Multi-Horizon Training & Evaluation Engine**:  
  `d:/weather_forcasting/phase7_forecasting/scripts/run_phase7_multi_horizon_engine.py`  
  *Role*: Trains direct horizon models across $h \in \{1, \dots, 12\}$ for temperature (avg, min, max), wind, pressure, rainfall amount, and rain binary occurrence. Generates empirical residual quantiles and 10-bin calibration diagnostics.
- **Operational Ingestion & Timeline Generator**:  
  `d:/weather_forcasting/phase7_forecasting/scripts/operational_ingestion_service.py`  
  *Role*: Retrieves $D-12 \dots D0$ observations via canonical panel lookup or live Open-Meteo API query. Emits 25-day operational contract.
- **Precomputed Timeline Seed Generator**:  
  `d:/weather_forcasting/phase7_forecasting/scripts/generate_25day_timeline_snapshots.py`  
  *Role*: Generates development snapshots for representative stations across both replay and live modes.
- **Automated Verification Test Suite**:  
  `d:/weather_forcasting/tests/test_phase7_multi_horizon_and_operational_timeline.py`  
  *Role*: Automated regression suite testing immutability, metrics fidelity, horizon structure, uncertainty coverage, and schema adherence.

### 1.2 Model Artifacts
Located in `d:/weather_forcasting/phase7_forecasting/models/`:
- `xgb_temp_h1.json`, `xgb_temp_h3.json`, `xgb_temp_h7.json`, `xgb_temp_h12.json` (Direct temperature regressors)
- `xgb_rain_cls_h1.json`, `xgb_rain_cls_h3.json`, `xgb_rain_cls_h7.json`, `xgb_rain_cls_h12.json` (Direct rain binary classifiers)

### 1.3 Authoritative Evaluation & Data Payloads
- `d:/weather_forcasting/phase7_forecasting/data/phase7_multi_horizon_evaluation_summary.json` (Backend evaluation ledger)
- `d:/weather_forcasting/frontend/src/data/authoritativeMultiHorizonSummary.json` (Frontend client mirror)
- `d:/weather_forcasting/frontend/src/data/authoritative25DayTimeline.json` (Dual-mode timeline payload: replay vs operational)
- `d:/weather_forcasting/phase4_database/schemas/timeline_25day.schema.json` (Strict JSON Schema validation)

### 1.4 Frontend Presentation Layer
- `d:/weather_forcasting/frontend/src/pages/ForecastPage.tsx`
- `d:/weather_forcasting/frontend/src/components/weather/OperationalTimeline25Day.tsx`
- `d:/weather_forcasting/frontend/src/components/weather/CurrentConditionsD0Panel.tsx`
- `d:/weather_forcasting/frontend/src/components/weather/ForecastDegradationChart.tsx`
- `d:/weather_forcasting/frontend/src/components/weather/ModelTransparencyDrawer.tsx`
- `d:/weather_forcasting/frontend/src/services/forecastService.ts`

---

## 2. Key Audit Observations & Focus Areas

1. **Probability Generation in Operational Generator (`operational_ingestion_service.py`)**:
   - In `operational_ingestion_service.py`, lines 219–221 currently compute:
     `rain_prob = round(float(max(0.04, min(0.85, 0.12 * np.exp(-0.15 * h) + 0.15 * (1 - np.exp(-0.15 * h))))), 3)`
   - **Critical Audit Finding**: The timeline generator used an analytic synoptic decay function anchored to winter base climatology ($0.12 \to 0.15$) resulting in probabilities clustered tightly around **12–14%** across all stations, rather than evaluating the station's actual feature vector $X_0$ through the trained XGBoost horizon classifiers `xgb_rain_cls_h{h}.json`!
   - This directly explains the user's inquiry regarding 12–14% rain probability clustering.
2. **Temperature Smoothing in Operational Generator**:
   - Lines 213–216 used an exponential decay formula from anchor temperature towards an idealized seasonal sine wave rather than running full XGBoost inference with station-specific lag and topography features.
3. **Audit Action Plan**:
   - Tasks 3–13 will rigorously audit this divergence between the validation engine (which trained actual XGBoost models across all horizons) and the runtime ingestion service, ensuring operational forecasts use true model inference while maintaining deterministic fallbacks.
