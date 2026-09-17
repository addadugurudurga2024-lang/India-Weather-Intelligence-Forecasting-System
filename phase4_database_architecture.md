# Phase 4 — Database Architecture Specification

## MongoDB Application Data Layer & Security Boundary

---

### 1. Executive Summary

Phase 4 establishes the database architecture for the **India Weather Forecasting & Intelligence System**. The database selected for the application read-optimized and metadata tier is **MongoDB** (Target Database: `india_weather_intelligence`).

This architecture implements a strict separation of concerns:
1. **Raw Source-of-Truth**: The audited Excel/Parquet dataset created in Phase 1 and curated in Phase 2 remains the permanent, immutable scientific baseline.
2. **Application Read Layer (MongoDB)**: Designed for high-speed spatial-temporal filtering, dashboard KPI queries, station profiles, and model inference record lookups.
3. **Security Boundary**: Web clients **NEVER** possess direct database credentials or direct network access to MongoDB. All data access routes exclusively through the future Phase 8 FastAPI service.

---

### 2. Physical & Logical Data Model

```text
┌────────────────────────────────────────────────────────┐
│             Database: india_weather_intelligence      │
└────────────────────────────────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   stations   │    │ weather_obs  │    │forecast_res  │    │model_metadata│
│ (413 Records)│    │(Time-Series) │    │ (Inference)  │    │  (6 Models)  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

#### 2.1 Collection: `stations`
* **Purpose**: Directory of all canonical physical weather monitoring stations across India.
* **Cardinality**: Exactly 413 stations (reconciled during Phase 1.5 and Phase 2.1).
* **Key Fields**:
  - `station_id`: String (Canonical composite key e.g., `"agartala_23.8833_91.2500_15m"`).
  - `station_name`: String (e.g., `"Agartala"`).
  - `state`: String (2-character ISO / IMD state code e.g., `"TR"`).
  - `district`: String (e.g., `"West Tripura"`).
  - `location`: GeoJSON `Point` (`{"type": "Point", "coordinates": [longitude, latitude]}`).
  - `elevation_m`: Number (Elevation above mean sea level in meters).
  - `operational_start`: Date / String ISO (`"2015-01-01"`).
  - `operational_end`: Date / String ISO (`"2025-02-10"`).
  - `record_count_total`: Integer (Total historical daily records).

#### 2.2 Collection: `weather_observations`
* **Purpose**: High-throughput storage of daily surface telemetry records.
* **Key Fields**:
  - `station_id`: String (Foreign reference to `stations.station_id`).
  - `date`: Date / ISO string (`"YYYY-MM-DD"`).
  - `avg_temp_c`: Number (Mean surface temperature in °C).
  - `min_temp_c`: Number (Minimum diurnal temperature in °C).
  - `max_temp_c`: Number (Maximum diurnal temperature in °C).
  - `wind_speed_kmh`: Number (Wind speed in km/h).
  - `air_pressure_hpa`: Number (Atmospheric pressure in hPa).
  - `rainfall_mm`: Number or `null` (**CRITICAL**: Missing rainfall is explicitly preserved as `null`, never 0.0).
  - `season`: String (`"Winter"`, `"Pre-Monsoon"`, `"Monsoon"`, `"Post-Monsoon"`).
  - `quality_flags`: Object with boolean sensor check flags (`temp_plausible`, `pressure_valid`, `rain_recorded`).

#### 2.3 Collection: `forecast_results`
* **Purpose**: Persistence of multi-model inference outputs for future historical verification.
* **Key Fields**:
  - `station_id`: String.
  - `forecast_date`: Date / ISO string.
  - `target`: String (`"target_a_temperature"`, `"target_b_rainfall_amount"`, `"target_c_rain_binary"`).
  - `prediction`: Number (Forecasted temperature in °C, rainfall in mm, or binary probability).
  - `prediction_unit`: String (`"celsius"`, `"mm"`, `"probability"`).
  - `model_name`: String (`"XGBoost-Regressor"`, `"LSTM-Sequence"`, etc.).
  - `model_version`: String (`"v1.0.0"`).
  - `generated_at`: Date / ISO timestamp.

#### 2.4 Collection: `model_metadata`
* **Purpose**: Machine-readable registry of trained model artifacts, cross-validation metrics, and holdout benchmarks.
* **Key Fields**:
  - `model_id`: String (Unique identifier e.g., `"xgb_temp_v1"`).
  - `model_name`: String.
  - `model_family`: String (`"gradient_boosted_trees"`, `"recurrent_neural_network"`, `"baseline"`).
  - `target`: String.
  - `metrics`: Object containing Fold 1, Fold 2, and 2025 holdout scores (`mae`, `rmse`, `r2`, `accuracy`, `roc_auc`).
  - `artifact_path`: Relative filesystem path to `.json` or `.pt` weight file.
  - `status`: String (`"production_candidate"` or `"benchmark"`).

---

### 3. Production Indexing Strategy (`indexes.js`)

To ensure sub-millisecond query latencies when querying millions of historical records, the following compound and specialized indexes are defined:

```javascript
// stations
db.stations.createIndex({ "station_id": 1 }, { unique: true });
db.stations.createIndex({ "state": 1, "district": 1 });
db.stations.createIndex({ "location": "2dsphere" });

// weather_observations
db.weather_observations.createIndex({ "station_id": 1, "date": -1 }, { unique: true });
db.weather_observations.createIndex({ "date": -1 });
db.weather_observations.createIndex({ "station_id": 1, "rainfall_mm": 1 });

// forecast_results
db.forecast_results.createIndex({ "station_id": 1, "forecast_date": 1, "target": 1, "model_name": 1 });
db.forecast_results.createIndex({ "generated_at": -1 });

// model_metadata
db.model_metadata.createIndex({ "model_name": 1, "target": 1, "version": 1 }, { unique: true });
```

---

### 4. BSON Schema Validation

To guarantee data integrity at the database layer, JSON schemas conforming to MongoDB `$jsonSchema` have been implemented:
* `phase4_database/schemas/stations.schema.json`
* `phase4_database/schemas/weather_observations.schema.json`
* `phase4_database/schemas/forecast_results.schema.json`
* `phase4_database/schemas/model_metadata.schema.json`

These schemas strictly enforce data types, coordinate bounds (India latitude: 6° to 38° N, longitude: 68° to 98° E), valid seasons, and non-negativity constraints for physical parameters.

---

### 5. Deterministic Development Seed Generation

To allow instant bootstrapping and local testing:
* Generator Script: `phase4_database/seed_development_db.py`
* Seed Files:
  - `phase4_database/seeds/stations.seed.json`: 413 physical stations exported directly from Phase 2 canonical data with full GeoJSON formatting.
  - `phase4_database/seeds/model_metadata.seed.json`: 6 authoritative Phase 3 model configurations and exact holdout metrics.

---

### 6. Security Architecture & Environment Isolation

1. **Direct Connection Prohibition**: Under no circumstances does the browser communicate directly with MongoDB. All requests terminate at the FastAPI REST boundary.
2. **Credential Management**:
   - Connection strings are parameterized via environment variables (`MONGODB_URI`, `MONGODB_DATABASE`).
   - `.env` files are strictly excluded via `.gitignore`.
   - `.env.example` templates are provided with dummy credentials.
3. **Compass Workflow**: Developers use MongoDB Compass for administrative and debugging operations using local loopback (`mongodb://localhost:27017`) without exposing credentials.
