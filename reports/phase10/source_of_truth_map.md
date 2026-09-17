# Phase 10 — System Source-of-Truth Integration Map

**Project:** India Weather Forecasting & Intelligence System  
**Phase:** Phase 10 — Full-Stack Integration Ready  
**Purpose:** Prevent duplicate, out-of-sync, or contradictory data pathways across frontend, backend, services, and ML models.

---

## Authoritative System Matrix

| Feature Domain | Backend API Route | Application Service Adapter | Ground-Truth Data / Model Artifact | Frontend Consumer Component / Page |
| :--- | :--- | :--- | :--- | :--- |
| **Stations Registry** | `GET /api/v1/stations`<br>`GET /api/v1/stations/{id}` | `backend.app.services.data_service.get_station_registry` | `phase2_canonical/outputs/canonical_stations.json` (413 stations) | `FilterContext.tsx`, `StationsPage.tsx`, `StationSelect.tsx` |
| **State / District Hierarchy** | `GET /api/v1/stations/hierarchy` | `backend.app.services.data_service.get_geographic_hierarchy` | `phase2_canonical/outputs/authoritative_district_mapping.json` | Cascading Dropdowns in `ForecastPage`, `LongTermPredictorPage` |
| **Historical Analytics** | `GET /api/v1/analytics/summary`<br>`GET /api/v1/analytics/timeseries` | `backend.app.services.data_service.get_historical_analytics` | `phase2_canonical/outputs/canonical_weather_full.parquet` | `AnalyticsPage.tsx`, `RainfallPage.tsx`, `DashboardPage.tsx` |
| **Map Geospatial Layers** | `GET /api/v1/stations/geo` | `backend.app.services.data_service.get_geospatial_station_data` | `canonical_stations.json` + `canonical_weather_full.parquet` | `MapPage.tsx`, `MapComponent.tsx` |
| **Operational Forecast (T+1 → T+12)** | `GET /api/v1/forecast/multi-horizon` | `phase7_forecasting.scripts.operational_ingestion_service.run_multi_horizon_direct_forecast` | 84 Frozen XGBoost Models (`phase7_forecasting/models/xgb_{target}_h{1..12}.json`) | `ForecastPage.tsx`, `ForecastCard.tsx` |
| **25-Day Timeline (D-12 → D0 → D+12)** | `GET /api/v1/forecast/25day-timeline` | `phase7_forecasting.scripts.operational_ingestion_service.build_operational_timeline` | Past observations (`OBSERVED`), D-1 model estimate (`MODEL ESTIMATE`), D0 telemetry (`CURRENT` or `UNAVAILABLE`), future $T+1..T+12$ (`MODEL ESTIMATE`) | `ForecastPage.tsx` (25-day timeline chart & table) |
| **D0 Current Observation** | `GET /api/v1/forecast/current-telemetry` | `phase7_forecasting.scripts.operational_ingestion_service.get_station_feature_state` | Ground truth observation only; **Strictly NO model fallback** | `ForecastPage.tsx`, `WeatherCard.tsx` |
| **AI Weather Intelligence** | `POST /api/v1/intelligence/query`<br>`GET /api/v1/intelligence/summary`<br>`GET /api/v1/intelligence/risk` | `phase8_intelligence.core.qa_interface.QAInterface`<br>`phase8_intelligence.core.engine.IntelligenceEngine` | Verified observations + Phase 7 multi-horizon forecasts + grounding validator | `AIIntelligenceCard.tsx`, `IntelligenceModal.tsx`, `DashboardPage.tsx` |
| **Long-Term Weather Predictor** | `POST /api/v1/long-term-predictor/predict`<br>`GET /api/v1/long-term-predictor/climatology` | `phase9_long_term_predictor.services.long_term_predictor_engine.LongTermPredictorEngine` | 7 Frozen XGBoost Models (`phase9_long_term_predictor/models/xgb_longterm_*_v1.json`) + `station_climatology_413.json` | `LongTermPredictorPage.tsx` |
| **Model Registry & Cards** | `GET /api/v1/models/registry` | `backend.app.services.model_service.get_model_registry` | `phase3_models/metrics/phase3_authoritative_metrics.json`, Phase 7 & Phase 9 metadata | `ModelsPage.tsx` |

---

## Architectural Rules for Single Source-of-Truth

1. **Station Identity Integrity:**
   `station_id` is the universal, immutable identifier across all 413 stations (e.g., `rajahmundry_rjnagaram_17.1104_81.8182_46m`). No synthetic station IDs are permitted.
2. **D0 Observation-Only Invariant:**
   $D0$ telemetry represents physical observation at forecast origin $t_0$. If telemetry is absent, it is explicitly marked `UNAVAILABLE`. No ML fallback is ever substituted for $D0$.
3. **Horizon-Specific Model Routing:**
   Short-term operational forecasts for horizons $h \in \{1 \dots 12\}$ route strictly to the corresponding `xgb_{target}_h{h}.json` model trained for that horizon. No extrapolation beyond $T+12$.
4. **Long-Term Decoupling:**
   Long-term calendar date predictions route strictly to Phase 9 climatological XGBoost models (`xgb_longterm_*_v1.json`). They do not overwrite or alias short-term operational forecasts.
5. **Physical Consistency Enforcement:**
   Outputs across both short-term and long-term systems strictly satisfy:
   - $T_{\min} \le T_{\text{avg}} \le T_{\max}$
   - $\text{Rainfall} \ge 0$
   - $\text{Wind Speed} \ge 0$
   - $\text{Rain Probability} \in [0, 1]$
