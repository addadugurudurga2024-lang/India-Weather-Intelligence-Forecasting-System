# Phase 10 Authoritative API Route Inventory

**Project:** India Weather Forecasting & Intelligence System  
**Phase:** Phase 10 — Full-Stack Integration Ready  
**Base URL:** `/api/v1`  
**Protocol:** REST / JSON over HTTP  

---

## 1. System Health & Metadata

### `GET /api/v1/health`
- **Purpose:** System readiness, liveness check, and subsystem asset verification.
- **Request Parameters:** None
- **Response Schema:**
  ```json
  {
    "status": "HEALTHY",
    "system": "India Weather Forecasting & Intelligence System",
    "environment": "development",
    "canonical_stations_count": 413,
    "phase7_models_verified": 84,
    "phase9_models_verified": 7
  }
  ```
- **Service Used:** `backend.app.services.data_service.load_stations`
- **Error Behavior:** 500 if critical singletons fail to load.

---

## 2. Stations & Geographic Registry

### `GET /api/v1/stations`
- **Purpose:** Retrieve all 413 canonical weather monitoring stations.
- **Query Parameters:**
  - `state` (optional string): Filter stations by Indian state.
  - `district` (optional string): Filter stations by district.
- **Response Schema:**
  ```json
  {
    "total_stations": 413,
    "stations": [
      {
        "station_id": "string",
        "station_name": "string",
        "state": "string",
        "district": "string",
        "latitude": 0.0,
        "longitude": 0.0,
        "elevation_m": 0.0
      }
    ]
  }
  ```
- **Service Used:** `backend.app.services.data_service.load_stations`

### `GET /api/v1/stations/hierarchy`
- **Purpose:** Returns nested State → District → Stations tree for cascading frontend selectors.
- **Response Schema:** Map of `{ [state: string]: { [district: string]: StationBase[] } }`
- **Service Used:** `backend.app.services.data_service.get_geographic_hierarchy`

### `GET /api/v1/stations/{station_id}`
- **Purpose:** Retrieve metadata for a single station by canonical ID.
- **Path Parameters:** `station_id` (string)
- **Response Schema:** `StationBase` object.
- **Error Behavior:** 404 with structured message if `station_id` not in 413 canonical registry.

---

## 3. Historical Analytics

### `GET /api/v1/analytics/summary/{station_id}`
- **Purpose:** Aggregated multi-year climatological statistics and historical records for a station.
- **Path Parameters:** `station_id` (string)
- **Response Schema:**
  ```json
  {
    "station_id": "string",
    "station_name": "string",
    "record_count": 3693,
    "date_range": { "start": "2015-01-01", "end": "2025-02-10" },
    "temp_avg_mean": 27.4,
    "temp_min_record": 14.2,
    "temp_max_record": 44.8,
    "annual_rainfall_mean_mm": 1050.5,
    "max_single_day_rain_mm": 128.4,
    "wind_speed_mean_kmh": 6.8,
    "air_pressure_mean_hpa": 1009.2
  }
  ```
- **Data Source:** `phase2_canonical/outputs/canonical_weather_full.parquet`

### `GET /api/v1/analytics/timeseries/{station_id}`
- **Purpose:** Daily historical observations up to specified limit.
- **Query Parameters:** `limit` (integer, default 365, max 3650)
- **Response Schema:** Array of daily observation points (`date`, `temp_avg`, `temp_min`, `temp_max`, `rainfall`, `wind_speed`, `air_pressure`).

---

## 4. Operational Forecast Center (Phase 7 / Phase 8.5)

### `GET /api/v1/forecast/25day-timeline/{station_id}`
- **Purpose:** Complete 25-day operational timeline spanning D-12 to D+12 around forecast origin $t_0$.
- **Path Parameters:** `station_id` (string)
- **Response Schema:**
  ```json
  {
    "station_id": "string",
    "station_name": "string",
    "state": "string",
    "district": "string",
    "forecast_origin": "2025-02-10",
    "timeline_days_count": 25,
    "timeline": [
      {
        "date": "2025-02-10",
        "day_offset": 0,
        "horizon_label": "D0",
        "provenance": "CURRENT",
        "temp_avg_c": 26.5,
        ...
      }
    ]
  }
  ```
- **Provenance Rules:**
  - `D-12` to `D-1`: `OBSERVED` or `MODEL ESTIMATE` (for D-1 prior to 24h lag close)
  - `D0`: Strictly `CURRENT` (physical telemetry) or `UNAVAILABLE` (**NO model fallback**)
  - `D+1` to `D+12`: `MODEL ESTIMATE` (Phase 7 direct XGBoost models)

### `GET /api/v1/forecast/multi-horizon/{station_id}`
- **Purpose:** Direct multi-horizon forecasts $T+1$ through $T+12$ evaluated on the 84 trained Phase 7 models.
- **Path Parameters:** `station_id` (string)
- **Response Schema:** List of 12 horizon predictions with physical bounds and model attribution.

### `GET /api/v1/forecast/current-telemetry/{station_id}`
- **Purpose:** Direct access to $D0$ physical telemetry.
- **Error Behavior:** Returns `provenance: "UNAVAILABLE"` with `null` fields if station is missing real-time observation.

---

## 5. AI Weather Intelligence (Phase 8)

### `POST /api/v1/intelligence/query`
- **Purpose:** Zero-hallucination meteorological natural-language question answering.
- **Request Body:**
  ```json
  {
    "station_id": "rajahmundry_rjnagaram_17.1104_81.8182_46m",
    "question": "Will rain occur in the next 3 days?"
  }
  ```
- **Response Schema:**
  ```json
  {
    "station_id": "string",
    "question": "string",
    "intent": "RAIN_OCCURRENCE",
    "answer": "string",
    "grounding_status": "GROUNDED",
    "evidence": ["string"],
    "limitations": null
  }
  ```
- **Guardrails:** Automatically rejects queries on unsupported variables (humidity, cloud cover, AQI, hourly timing).

### `GET /api/v1/intelligence/summary/{station_id}`
- **Purpose:** Full natural language executive summary, temperature insights, rainfall insights, and controlled confidence language.

### `GET /api/v1/intelligence/risk/{station_id}`
- **Purpose:** Precipitation and meteorological risk classification (`LOW`, `MODERATE`, `HIGH`) with grounded rationale.

---

## 6. Long-Term Weather Predictor (Phase 9)

### `POST /api/v1/long-term-predictor/predict`
- **Purpose:** Climatological and harmonic XGBoost inference for any future calendar date (2025-01-01 to 2027-12-31).
- **Request Body:**
  ```json
  {
    "station_id": "rajahmundry_rjnagaram_17.1104_81.8182_46m",
    "target_date": "2026-11-15"
  }
  ```
- **Response Schema:**
  ```json
  {
    "status": "AVAILABLE",
    "prediction_type": "Long-Term Historical / Seasonal Model Estimate",
    "prediction_date": "2026-11-15",
    "station_id": "string",
    "station_name": "string",
    "predictions": {
      "average_temperature_c": 25.2,
      "minimum_temperature_c": 19.8,
      "maximum_temperature_c": 30.6,
      "rainfall_amount_mm": 1.4,
      "rain_probability_pct": 22.0,
      "wind_speed_kmh": 4.8,
      "air_pressure_hpa": 1012.3
    },
    "uncertainty_intervals": {
      "avg_temp_interval_80": [23.1, 27.4],
      "method": "Empirical residual quantiles from 2024 out-of-time walk-forward validation"
    },
    "historical_reference": { ... },
    "explainability_trace": [ ... ],
    "provenance": { ... },
    "scientific_limitations": [ ... ]
  }
  ```
- **Physical Constraints:** $T_{\min} \le T_{\text{avg}} \le T_{\max}$, $\text{Rainfall} \ge 0$, $\text{Wind} \ge 0$, $\text{Rain Probability} \in [0, 100]\%$.

### `GET /api/v1/long-term-predictor/climatology/{station_id}`
- **Purpose:** Station-specific multi-year and 12-month baseline climatological stats.

### `GET /api/v1/long-term-predictor/metadata`
- **Purpose:** Model cards, evaluation metrics, and feature schemas for Phase 9 models.

---

## 7. Model Registry

### `GET /api/v1/models/registry`
- **Purpose:** Comprehensive registry containing Phase 3 baseline metrics, Phase 7 multi-horizon metadata, and Phase 9 long-term model details.
