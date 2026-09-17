# Phase 7 — Current & Recent Meteorological Data Source Audit

**Project**: India Weather Forecasting & Intelligence System  
**Phase**: PHASE 7 — Operational 25-Day Weather Timeline + 12-Day Multi-Horizon Forecasting  
**Authoritative Date**: 2026-09-13  
**Status**: APPROVED DATA SOURCE AUDIT (Task 20)  

---

## 1. Problem Statement: The Temporal Gap

The canonical Phase 2 dataset derived from the Kaggle IMD repository concludes on **2025-02-10**. Consequently:
- For any operational date beyond 2025-02-10 (including the current operational date `2026-09-13`), the canonical dataset alone cannot provide actual recorded measurements for the historical retrospective window ($D-12 \dots D-1$) or current day ($D0$).
- In strict adherence to the **Zero Fabrication Rule**, the system must never synthesize, interpolate, or guess these values.
- If an approved external source cannot be reached or is missing coverage for a station, the system must return `null` with status `"UNAVAILABLE"`.

---

## 2. Comparative Evaluation of Meteorological Ingestion Candidates

| Evaluation Criteria | Candidate 1: IMD AWS Portal (`mausam.imd.gov.in`) | Candidate 2: Open-Meteo Archive & Forecast APIs | Candidate 3: OpenWeatherMap / Commercial APIs |
| :--- | :--- | :--- | :--- |
| **Data Provenance & Authority** | Direct primary national meteorological agency of India. | WMO GTS (Global Telecommunication System), ECMWF IFS, GFS, IMD station assimilation. | Commercial third-party aggregator. |
| **Licensing & Legal Status** | Open Government Data (OGD) India, but lacks automated API key access for programmatic bulk queries. | **Creative Commons Attribution 4.0 International (CC BY 4.0)**; Open Database License (ODbL). Non-commercial open access. | Proprietary commercial license; strict rate limits; expensive tiering. |
| **Station Coordinate Alignment** | Station name matching required; high rate of name spelling variations across portals. | **Exact decimal coordinate queries** (`latitude`, `longitude`) aligning with all 413 canonical station GPS positions. | City-level centroids; poor rural/alpine station resolution. |
| **Supported Variables** | Temp (Max/Min), Rainfall, Wind, RH, Pressure. | Daily mean, min, max temperature ($^\circ\text{C}$), wind speed ($\text{km/h}$), surface pressure ($\text{hPa}$), precipitation sum ($\text{mm}$). | Temperature, pressure, wind, clouds. Often synthesizes missing values. |
| **Historical Backfill ($D-12 \dots D-1$)** | Web portal only displays recent 24–48 hours; archives require manual form submissions. | **Full historical archive API** (`archive-api.open-meteo.com`) providing exact historical daily measurements. | Archive data locked behind high-cost enterprise tier. |
| **API Reliability & Latency** | Frequent 502/504 downtime; session token requirements; scraping required. | High-availability CDN; sub-50ms global latency; HTTP 200 validated during reconnaissance. | Reliable, but API key management overhead. |
| **Verdict** | **INSUFFICIENT FOR AUTOMATED SERVING** (Used as validation cross-check) | **APPROVED AS AUTHORITATIVE OPERATIONAL SOURCE** | **REJECTED** (Proprietary, poor rural coverage) |

---

## 3. Approved Source Technical Profile: Open-Meteo

1. **Endpoint Specifications**:
   - Historical Archive ($D-12 \dots D-1$):  
     `https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={d_minus_12}&end_date={d_minus_1}&daily=temperature_2m_mean,temperature_2m_min,temperature_2m_max,precipitation_sum,wind_speed_10m_max,surface_pressure&timezone=auto`
   - Current Conditions ($D0$):  
     `https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,surface_pressure&timezone=auto`
2. **Variable Reconciliation**:
   - `temperature_2m_mean` $\longleftrightarrow$ `avg_temp_clean` ($^\circ\text{C}$)
   - `temperature_2m_min` $\longleftrightarrow$ `min_temp_clean` ($^\circ\text{C}$)
   - `temperature_2m_max` $\longleftrightarrow$ `max_temp_clean` ($^\circ\text{C}$)
   - `precipitation_sum` $\longleftrightarrow$ `rainfall` ($\text{mm}$)
   - `wind_speed_10m_max` $\longleftrightarrow$ `wind_speed` ($\text{km/h}$)
   - `surface_pressure` $\longleftrightarrow$ `air_pressure` ($\text{hPa}$)
3. **Attribution & Licensing Requirements**:
   - Every response payload must include: `"provenance": "Open-Meteo Open Weather API (CC BY 4.0 / WMO GTS)"`.
   - UI must expose data source transparency in the D0 panel.

---

## 4. Operational Ingestion & Zero-Fabrication Fallback Policy

```
[Inference Request for Station S, Date D0]
                   |
                   v
   Is D0 <= 2025-02-10 (Historical Ground Truth)?
        /                                 \
      YES                                 NO (Operational 2026 Date)
      /                                     \
Fetch from Phase 2                      Query Open-Meteo API
Canonical Parquet                       using Station (lat, lon)
      |                                              |
      v                                              v
Status: "OBSERVED"                           Did API return 200 & valid data?
Provenance: "Phase 2 IMD Canonical"                 /                  \
                                                  YES                  NO / Offline
                                                  /                      \
                                        Status: "OBSERVED"         Status: "UNAVAILABLE"
                                        Provenance: "Open-Meteo"   All fields: null
                                                                   UI: "CURRENT DATA UNAVAILABLE"
```

Under NO circumstance will the system:
1. Impute missing past observations using linear interpolation across missing days.
2. Run ML models backward to fill historical observations.
3. Label unverified synthetic numbers as actual readings.
