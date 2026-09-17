# India Weather Forecasting & Intelligence System

A production-oriented, scientific weather intelligence and forecasting platform covering **413 canonical physical weather stations across 32 Indian States and Union Territories**.

---

## 1. Project Phase Status

```text
PHASE 1   → PASS (Dataset Audit, Quality Assessment & Profiling)
PHASE 1.5 → VERIFIED (Reconciliation & Pre-Phase 2 Gate)
PHASE 2   → COMPLETE (Data Cleaning, Feature Engineering & Canonicalization)
PHASE 2.1 → RECONCILED / PRE-MODEL GATE PASSED (413 Physical Stations Verified)
PHASE 3   → PASS (Forecasting Model Development, Walk-Forward Validation & Benchmarking)
PHASE 4   → PASS (React + TypeScript Web Application & MongoDB Foundation)
PHASE 4.1 → COMPLETE & VERIFIED (MongoDB Development Seed Execution)
PHASE 5   → COMPLETE & VERIFIED (Maps & Advanced Geospatial Visualization)
PHASE 6   → COMPLETE & VERIFIED (Model Evaluation, Benchmarking & Explainability)
```

---

## 2. Geospatial Intelligence & Interactive Maps (`frontend/src/components/maps/`)

Built natively with lightweight, high-performance pure SVG rendering:
* **413 Canonical Physical Stations**: Real-time rendering of all stations with zoom-responsive scaling, hover halos, and pulsing focus beacons.
* **Calibrated Equirectangular Projection**: Precisely calibrated to India subcontinent bounds (`6.5°N–37.5°N`, `68.0°E–97.5°E`) with national and state boundary geometry.
* **6 Thematic Geospatial Layers**:
  - `Stations`: Full network telemetry overview with elevation and focus states.
  - `Temperature`: Thermal color ramps (<5°C to ≥34°C) with average, minimum, and maximum toggles.
  - `Rainfall`: IMD scientific precipitation classification (Very Light to Very Heavy) with strict missing data distinction (`null !== 0.0 mm`).
  - `Elevation`: Hypsometric topography tints (High Himalayan, Sub-Himalayan, Deccan, Plains).
  - `State Density`: Regional station density choropleth with explicitly labeled derived aggregates.
  - `XGBoost Forecast Overlay`: Direct visualization of Phase 3 next-day temperature, rainfall, and rain probability predictions.
* **Temporal Scrubber & Animation**: Play/pause animation and timeline scrubber across 41 continuous 2025 observation dates with 1x, 2x, 4x speed controls.
* **Multi-Location Comparison**: Side-by-side comparative inspection drawer evaluating 2 or 3 stations across altitude, observed telemetry, and holdout forecasts.
* **Global Filter Synchronization**: Seamless bi-directional interaction between map clicks and the global `FilterContext`.

---

## 2. Frontend Application (`frontend/`)

Built with **React 19**, **TypeScript 6**, and **Vite 8**:
* **Zero Bloat**: Lightweight, pure SVG responsive data visualizations.
* **Themes**: Accessible Dark and Light mode design system with custom HSL tokens.
* **10 Dedicated Routes**:
  - `/dashboard` — Executive command center and real-time surface telemetry
  - `/analytics` — Diurnal temperature curves, min/max envelopes, and anomaly highlights
  - `/forecast` — Forward forecast comparisons across XGBoost, LSTM, and Persistence baselines
  - `/rainfall` — Hyetographs, monthly precipitation, and IMD rainy-day distribution
  - `/stations` — 413 canonical physical weather stations directory and telemetry
  - `/map` — Geographic station map layout with zoom/pan and elevation heat styling
  - `/models` — Phase 3 model benchmarking (MAE, RMSE, R², Accuracy, ROC-AUC)
  - `/data` — Paginated, searchable, sortable data explorer grid
  - `/methodology` — Audit trail, data hygiene rules, and validation splits
* **Global Search & Filter Bar**: Keyboard-driven (`Cmd+K` / `Ctrl+K`) searching across states, districts, and stations with cascading filters.

### Running the Frontend Locally:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

To verify the production build:
```bash
npm run build
```

---

## 3. Database Application Layer (`phase4_database/`)

Target Database: **`india_weather_intelligence`**
* **Collections**: `stations`, `weather_observations`, `forecast_results`, `model_metadata`.
* **Schemas**: BSON JSON schemas located in `phase4_database/schemas/`.
* **Production Indexes**: High-performance compound and 2dsphere indexes in `phase4_database/indexes.js`.
* **Seed Data**: Deterministic development seeds for 413 stations and 6 model artifacts in `phase4_database/seeds/`.
* **Compass Guide**: Complete workflow instructions in `phase4_database/MONGODB_COMPASS_GUIDE.md`.

---

## 4. Phase 3 Scientific Model Benchmark Highlights

| Target Variable | Metric | Baseline | XGBoost Regressor | PyTorch LSTM | Primary Candidate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Temperature** | Holdout MAE | 0.7235°C | 0.6527°C | **0.6441°C** | **XGBoost** (Production) / LSTM (Benchmark) |
| **Rainfall Amount** | Holdout MAE | 0.5026 mm | **0.4344 mm** | 0.4368 mm | **XGBoost** (Overall) / LSTM (Rainy Days) |
| **Rain Binary** | Holdout Accuracy | 57.13% | **89.19%** | 88.32% | **XGBoost** (ROC-AUC: 0.8366) |

---

## 5. Security & Boundary Architecture

```text
┌──────────────────────────────┐
│ React + TypeScript Frontend  │
└──────────────┬───────────────┘
               │
               │ Future REST API (Phase 8)
               ▼
┌──────────────────────────────┐
│ FastAPI Backend — Phase 8    │
└──────────────┬───────────────┘
               │
               │ Internal / Privileged Wire Protocol
               ▼
┌──────────────────────────────┐
│ MongoDB Application Database │
└──────────────────────────────┘
```
* The browser never possesses direct credentials to MongoDB.
* All development previews are clearly flagged with warning banners.
* No live data or production backend endpoints are fabricated.
