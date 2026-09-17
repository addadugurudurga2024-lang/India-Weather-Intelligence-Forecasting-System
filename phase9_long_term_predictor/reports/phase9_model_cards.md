# Phase 9 Long-Term Weather Predictor — Model Cards

## Overview
This document contains the authoritative model cards for the 7 production-selected machine learning models comprising the **Phase 9 Long-Term Weather Predictor**.

---

## 1. Average Temperature Regressor (`xgb_longterm_temp_v1`)

- **Model ID:** `xgb_longterm_temp_v1`
- **Target Variable:** `avg_temp_clean` (Daily Average Temperature in °C)
- **Algorithm:** Gradient Boosted Decision Trees (XGBoost Regressor `tree_method='hist'`)
- **Version:** `v1.0.0`
- **Dataset Source:** Canonical Historical Weather Panel (`canonical_weather_full.parquet`)
- **Dataset SHA-256:** `e6a636777430f078b4d970f9f46e79efcece7f97b67dd186c30a755d2783cd84`
- **Training Period:** `2015-01-01` to `2023-12-31` (804,648 historical records)
- **Validation Period:** `2024-01-01` to `2024-12-31` (147,469 records)
- **Out-of-Time Holdout:** `2025-01-01` to `2025-02-10` (16,732 records)
- **Input Features (24):**
  - Continuous Calendar: `doy`, `doy_sin`, `doy_cos`, `doy_sin2`, `doy_cos2`, `month`, `season_code`
  - Geographic Metadata: `latitude`, `longitude`, `elevation`
  - Station Historical Climatology: `station_hist_avg_temp_mean`, `station_hist_min_temp_mean`, `station_hist_max_temp_mean`, `station_hist_wind_speed_mean`, `station_hist_air_pressure_mean`, `station_hist_rain_frequency`
  - Station Month-Specific Climatology: `station_month_avg_temp_mean`, `station_month_avg_temp_std`, `station_month_min_temp_mean`, `station_month_max_temp_mean`, `station_month_wind_speed_mean`, `station_month_air_pressure_mean`, `station_month_rain_frequency`, `station_month_rain_amount_mean`
- **Validation Performance (2024):**
  - MAE: **1.379°C** (vs. Seasonal Climatology Baseline: 1.500°C, 8.05% error reduction)
  - RMSE: **1.864°C** (vs. Baseline: 2.032°C)
  - $R^2$: **0.889**
- **Holdout Performance (2025):** MAE: **1.324°C**, RMSE: **1.722°C**, $R^2$: **0.896**
- **Uncertainty Quantification:** Empirical 80% Prediction Interval: `[-2.12°C, +2.24°C]`
- **Physical Ordering:** Subject to $T_{\min} \le T_{\text{avg}} \le T_{\max}$ post-processing constraint.
- **Intended Use:** Estimating expected historical/seasonal mean temperature for a given future calendar date and station.
- **Not Intended For:** Next-day or short-range convective storm tracking; replacing operational 12-day numerical models.

---

## 2. Minimum Temperature Regressor (`xgb_longterm_temp_min_v1`)

- **Model ID:** `xgb_longterm_temp_min_v1`
- **Target Variable:** `min_temp_clean` (Daily Minimum Temperature in °C)
- **Algorithm:** XGBoost Regressor (`tree_method='hist'`)
- **Version:** `v1.0.0`
- **Validation Performance (2024):** MAE: **1.463°C** (vs. Baseline: 1.564°C, 6.45% error reduction), RMSE: **1.992°C**, $R^2$: **0.893**
- **Holdout Performance (2025):** MAE: **1.808°C**, RMSE: **2.323°C**, $R^2$: **0.843**
- **Uncertainty:** Empirical 80% Prediction Interval: `[-1.76°C, +2.76°C]`

---

## 3. Maximum Temperature Regressor (`xgb_longterm_temp_max_v1`)

- **Model ID:** `xgb_longterm_temp_max_v1`
- **Target Variable:** `max_temp_clean` (Daily Maximum Temperature in °C)
- **Algorithm:** XGBoost Regressor (`tree_method='hist'`)
- **Version:** `v1.0.0`
- **Validation Performance (2024):** MAE: **1.753°C** (vs. Baseline: 1.858°C, 5.64% error reduction), RMSE: **2.370°C**, $R^2$: **0.823**
- **Holdout Performance (2025):** MAE: **1.725°C**, RMSE: **2.273°C**, $R^2$: **0.798**
- **Uncertainty:** Empirical 80% Prediction Interval: `[-2.65°C, +2.81°C]`

---

## 4. Rain Probability Classifier (`xgb_longterm_rain_cls_v1`)

- **Model ID:** `xgb_longterm_rain_cls_v1`
- **Target Variable:** `rain_binary` ($\ge 0.1$ mm daily precipitation)
- **Algorithm:** XGBoost Binary Classifier (`objective='binary:logistic'`)
- **Version:** `v1.0.0`
- **Validation Performance (2024):**
  - ROC-AUC: **0.8747** (vs. Seasonal Baseline: 0.8714)
  - Brier Score: **0.1400** (vs. Seasonal Baseline: 0.1422)
- **Holdout Performance (2025):** ROC-AUC: **0.7915**, Brier Score: **0.0977**, F1: **0.3201**
- **Uncertainty:** Calibrated posterior probability output ($0.0 \le p \le 1.0$)

---

## 5. Rainfall Amount Regressor (`xgb_longterm_rain_amt_v1`)

- **Model ID:** `xgb_longterm_rain_amt_v1`
- **Target Variable:** `rainfall` (Daily Rainfall Depth in mm)
- **Algorithm:** XGBoost Regressor (`tree_method='hist'`)
- **Version:** `v1.0.0`
- **Validation Performance (2024):** MAE: **4.744 mm** (vs. Baseline: 4.780 mm), RMSE: **10.996 mm**
- **Holdout Performance (2025):** MAE: **1.180 mm**
- **Uncertainty:** Empirical 80% Prediction Interval: `[-7.25 mm, +5.08 mm]` (non-negative floor enforced $\ge 0.0$ mm)
- **Known Limitations:** Extreme convective thunderstorm rainfall has high variance and cannot be predicted precisely on seasonal scales.

---

## 6. Wind Speed Regressor (`xgb_longterm_wind_v1`)

- **Model ID:** `xgb_longterm_wind_v1`
- **Target Variable:** `wind_speed` (km/h)
- **Algorithm:** XGBoost Regressor (`tree_method='hist'`)
- **Version:** `v1.0.0`
- **Validation Performance (2024):** MAE: **2.587 km/h**, RMSE: **3.723 km/h**, $R^2$: **0.512**
- **Holdout Performance (2025):** MAE: **2.374 km/h**, RMSE: **3.342 km/h**, $R^2$: **0.472**
- **Uncertainty:** Empirical 80% Prediction Interval: `[-2.38 km/h, +5.41 km/h]` (floor $\ge 0.0$ km/h)

---

## 7. Air Pressure Regressor (`xgb_longterm_pressure_v1`)

- **Model ID:** `xgb_longterm_pressure_v1`
- **Target Variable:** `air_pressure` (hPa)
- **Algorithm:** XGBoost Regressor (`tree_method='hist'`)
- **Version:** `v1.0.0`
- **Validation Performance (2024):** MAE: **1.856 hPa**, RMSE: **2.440 hPa**, $R^2$: **0.811**
- **Holdout Performance (2025):** MAE: **1.372 hPa**, RMSE: **1.764 hPa**, $R^2$: **0.558**
- **Uncertainty:** Empirical 80% Prediction Interval: `[-2.97 hPa, +2.90 hPa]`
