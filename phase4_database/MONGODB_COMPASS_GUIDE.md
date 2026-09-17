# MongoDB Compass Guide & Security Architecture

## India Weather Forecasting & Intelligence System — Phase 4

---

### 1. Architectural Model & Security Boundary

```text
┌────────────────────────────────────────────────────────┐
│             React + TypeScript Frontend                │
│  - No database drivers                                 │
│  - No connection strings or secrets                    │
│  - Reads purely via typed API Service Layer            │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / JSON (REST)
                            ▼
┌────────────────────────────────────────────────────────┐
│             FastAPI Backend (Phase 8)                  │
│  - Validates schemas                                   │
│  - Handles authentication and rate limits              │
│  - Holds server-side connection pool                   │
└───────────────────────────┬────────────────────────────┘
                            │ MongoDB Wire Protocol (Internal / Privileged)
                            ▼
┌────────────────────────────────────────────────────────┐
│             MongoDB Database Server                    │
│  - Database: india_weather_intelligence               │
│  - Indexed collections for read optimization           │
│  - Validated by BSON JSON-Schemas                      │
└────────────────────────────────────────────────────────┘
```

> **CRITICAL SECURITY RULE**:  
> The browser frontend **NEVER** connects directly to MongoDB. There are no MongoDB client drivers, passwords, or connection strings in frontend source code. All browser traffic communicates with the API service boundary.

---

### 2. Database & Collection Overview

* **Database Name**: `india_weather_intelligence`
* **Logical Collections**:
  1. `stations`: 413 canonical physical weather stations across 32 Indian States & UTs.
  2. `weather_observations`: Canonical historical observations (2015–2025) with missing rainfall preserved as `null`.
  3. `forecast_results`: Model inference outputs with target labels, predicted values, model provenance, and generation timestamps.
  4. `model_metadata`: Authoritative Phase 3 benchmarking metrics, hyperparameters, fold results, and holdout scores for XGBoost, LSTM, and Persistence baselines.

---

### 3. MongoDB Compass Connection Workflow

#### Step 1: Open MongoDB Compass
Launch MongoDB Compass on your local workstation.

#### Step 2: Connection String
Paste the standard local connection string into the **New Connection** bar:
```text
mongodb://localhost:27017
```
If using authentication:
```text
mongodb://weather_admin:your_secure_password_here@localhost:27017/india_weather_intelligence?authSource=admin
```
Click **Connect**.

#### Step 3: Select Database
From the left navigation panel, click on **`india_weather_intelligence`**.  
If the database has not been created yet, it will be automatically created when documents are inserted or collections are created.

#### Step 4: Import Seed Documents via Compass
You can import the deterministic development seeds created in `phase4_database/seeds/`:
1. In Compass, click on **Add Data** -> **Import JSON or CSV file**.
2. Select `phase4_database/seeds/stations.seed.json` and select collection `stations`.
3. Select `phase4_database/seeds/model_metadata.seed.json` and select collection `model_metadata`.
4. Click **Import**.

---

### 4. Index Creation & Performance Optimization

To apply the production indexes in MongoDB Compass:
1. Open the **`_mongosh`** tab at the bottom of the Compass window.
2. Select the database:
   ```javascript
   use india_weather_intelligence;
   ```
3. Load and execute `phase4_database/indexes.js`:
   ```javascript
   load("d:/weather_forcasting/phase4_database/indexes.js");
   ```

#### Index Summary:
- **`stations`**:
  - `{ "station_id": 1 }` (Unique)
  - `{ "state": 1, "district": 1 }`
  - `{ "location": "2dsphere" }` (Geospatial coordinate index)
- **`weather_observations`**:
  - `{ "station_id": 1, "date": -1 }` (Unique compound index)
  - `{ "date": -1 }`
  - `{ "station_id": 1, "rainfall": 1 }`
- **`forecast_results`**:
  - `{ "station_id": 1, "forecast_date": 1, "target": 1, "model_name": 1 }` (Compound index)
  - `{ "generated_at": -1 }`
- **`model_metadata`**:
  - `{ "model_name": 1, "target": 1, "version": 1 }` (Unique)

---

### 5. Seed Generation & Database Reset Workflow

To regenerate or refresh the development seed data:
```bash
# From workspace root:
python phase4_database/seed_development_db.py
```
This script reads the canonical Phase 2 station metadata (`phase2_curation/canonical_data/station_metadata.json`) and Phase 3 model registry (`phase3_modeling/artifacts/model_registry.json`) and regenerates clean, deterministic seed files:
- `phase4_database/seeds/seed_stations.json` (413 records)
- `phase4_database/seeds/seed_model_metadata.json` (6 records)

---

### 6. Credentials & Environment Variable Protection

1. **Never Commit Secrets**: Ensure `.env` is listed in `.gitignore`.
2. **Use Template Files**: Share configuration keys only via `.env.example`.
3. **Least Privilege**: When creating MongoDB users for Phase 8 FastAPI, grant read/write permissions only to `india_weather_intelligence`, with no cluster-admin privileges.
