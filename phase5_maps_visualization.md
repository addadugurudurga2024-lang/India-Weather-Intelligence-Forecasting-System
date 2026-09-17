# Phase 5 — Maps + Advanced Visualization Master Specification

## Executive Summary
Phase 5 transforms the initial geographic foundation into a production-grade, interactive geospatial intelligence engine for the **India Weather Forecasting & Intelligence System**. Operating across all **413 canonical physical weather stations**, the system couples authoritative 2025 meteorological observations with benchmarked **Phase 3 XGBoost holdout predictions** in a lightweight, pure SVG rendering architecture.

---

## 1. Authoritative Geospatial Data Foundations

### 1.1 Canonical Station Coverage
- **Station Count**: Exactly 413 physical meteorological stations established in Phase 2.
- **Geographic Extent**:
  - Latitude: 7.9833°N (Kanyakumari) to 34.0833°N (Srinagar)
  - Longitude: 68.8500°E (Dwarka) to 95.3833°E (Passighat)
  - Altitude: 0.0 m (coastal) to 2,652.0 m (Himalayan / Nilgiri summits)
- **Mathematical Projection**:
  - Calibrated Equirectangular (Plate Carrée) projection bounded to `[6.5, 37.5]°N` and `[68.0, 97.5]°E`.
  - Deterministic conversion to a `800 x 720` SVG coordinate space via `GeographicService.projectCoordinates`.

### 1.2 Meteorological Observations (2025 Modern Period)
- Extracted deterministically from `phase2_canonical/outputs/canonical_weather_forecasting.parquet`.
- 16,732 daily station observations spanning 41 continuous dates from `2025-01-01` to `2025-02-10`.
- **Zero Fabrication**: Every observed value originates from audited IMD records.
- **Strict Data Quality Integrity**: Missing observations are explicitly preserved as `null` and displayed in slate gray (`#64748b`) with explicit `"Missing / Not Reported"` tooltips. Missing rainfall is **never coerced to 0.0 mm**.

### 1.3 Phase 3 XGBoost Holdout Predictions
- Extracted directly from `phase3_models/predictions/` holdout parquets:
  - `xgb_temp_preds_holdout.parquet` (Next-day temperature regression)
  - `xgb_rain_preds_holdout.parquet` (Next-day rainfall amount regression)
  - `xgb_rain_cls_preds_holdout.parquet` (Next-day rain binary probability classification)
- Spans 40 dates across 409 reporting holdout stations.
- Prominently labeled as `"FORECAST — XGBOOST CANDIDATE"` to avoid conflation with physical observations.

---

## 2. Advanced Thematic Map Layers

The system provides six interactive visualization layers via `LayerControl.tsx`:

| Layer ID | Domain Variable | Scientific Scale / Classification | Unit | Data Quality Flag |
| :--- | :--- | :--- | :--- | :--- |
| `stations` | Network Telemetry | Physical stations, focus beacons, halos | — | `OBSERVED` |
| `temperature` | Observed Thermal | Continuous palette: `<5°C` (cold) to `≥34°C` (heat) | °C | `OBSERVED` / `MISSING` |
| `rainfall` | Precipitation | IMD standard classification: Very Light, Light, Moderate, Rather Heavy, Heavy, Very Heavy | mm | `OBSERVED` / `MISSING` (≠ 0mm) |
| `elevation` | Hypsometric Relief | High Himalayan (≥1500m), Sub-Himalayan (1000–1499m), Deccan (600–999m), Plains (<600m) | m | `OBSERVED` |
| `state_density`| Station Distribution | Regional density choropleth (1–4 tiers) | count | `DERIVED AGGREGATE` |
| `forecast_overlay` | Next-Day Model Output | Temperature, precipitation amount, rain risk probability | °C, mm, % | `XGBOOST FORECAST` |

---

## 3. Interactive Geospatial UX & Controls

1. **Continuous Zoom & Smooth Pan**:
   - Wheel zoom (0.75x to 4.0x) with bounds clamping.
   - Click-and-drag pan across the subcontinent.
   - Reset button and keyboard shortcuts (`+`, `-`, `0`, Arrow keys).
2. **Temporal Scrubber & Animation**:
   - Scrubber slider and calendar step buttons traversing valid 2025 dates.
   - Smooth temporal playback animation with variable speed controls (1x @ 1200ms, 2x @ 600ms, 4x @ 300ms).
3. **Multi-Location Comparison Drawer**:
   - Side-by-side comparison of up to 3 stations across altitude, observed telemetry, and next-day forecasts.
4. **Bi-directional Global Filter Synchronization**:
   - Selecting a station pin immediately updates `FilterContext` (`state`, `district`, `stationId`) and synchronizes with Station Explorer, Analytics, and Forecast Center.
