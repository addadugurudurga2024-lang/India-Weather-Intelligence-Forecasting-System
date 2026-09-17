# Phase 6 — Meteorological Model Cards & Scientific Limitations

## Executive Overview
This document provides production-grade model cards for the forecasting models developed in Phase 3 and evaluated in Phase 6 of the **India Weather Forecasting & Intelligence System**. 

The system benchmarks three model families across three distinct meteorological tasks:
1. **Persistence & Majority Baselines** (Naive physical and majority benchmarks)
2. **XGBoost Gradient Boosted Trees** (Approved production candidate)
3. **PyTorch LSTM Recurrent Neural Networks** (Deep sequence benchmark)

---

## 1. Model Card: XGBoost Production Candidate

### 1.1 Model Details
- **Developer**: Antigravity Engineering Team
- **Model Family**: Gradient Boosted Decision Trees (XGBoost v3.3.0)
- **Model Artifacts**:
  - Temperature: `phase3_models/xgboost/temperature/xgb_temp_fold2.json`
  - Rainfall Amount: `phase3_models/xgboost/rainfall/xgb_rain_amt_fold2.json` (Target: $\log(1 + \text{rainfall})$)
  - Rain Classification: `phase3_models/xgboost/rain_classification/xgb_rain_cls_fold2.json`
- **Model Status**: `APPROVED_FOR_PRODUCTION_CANDIDATE`

### 1.2 Intended Use
- **Primary Use**: 24-hour forward operational forecasting across 413 canonical weather stations in India.
- **Out-of-Scope Uses**: Sub-daily nowcasting ($<24\text{ hours}$), multi-week seasonal outlooks ($>7\text{ days}$), direct hurricane cyclone track steering, and automated life-critical flood alert dispatch without human meteorologist review.

### 1.3 Training & Validation Architecture
- **Validation Protocol**: Chronological Walk-Forward Expanding Window.
  - Fold 1: Train 2021–2022 (290k rows) $\rightarrow$ Validation 2023 (149k rows)
  - Fold 2: Train 2021–2023 (439k rows) $\rightarrow$ Validation 2024 (146k rows)
  - Final Isolated Holdout: `2025-01-01` to `2025-02-10` (16,322 station-days)
- **Input Features (26 Total)**:
  - Current day cleaned surface observations (`avg_temp_clean`, `min_temp_clean`, `max_temp_clean`, `wind_speed`, `air_pressure`, `rainfall`).
  - Geography & Altitude (`elevation`, `latitude`, `longitude`).
  - Periodic seasonal cycle encoding (`doy_sin`, `doy_cos`, `month_sin`, `month_cos`).
  - Autoregressive Lags (`lag_1_avg_temp`, `lag_2_avg_temp`, `lag_1_min_temp`, `lag_1_max_temp`, `lag_1_rainfall`, `lag_2_rainfall`, `lag_1_wind_speed`, `lag_1_air_pressure`).
  - Rolling windows (`rolling_3d_temp_mean`, `rolling_7d_temp_mean`, `rolling_7d_temp_std`, `rolling_3d_rainfall_sum`, `rolling_7d_rainfall_sum`).

### 1.4 Holdout Performance Summary
- **Target A (Temperature)**: $\text{MAE} = 0.6527^\circ\text{C}$, $\text{RMSE} = 0.9148^\circ\text{C}$, $R^2 = 0.9705$ (9.8% MAE reduction vs Persistence).
- **Target B (Rainfall Amount)**: Overall $\text{MAE} = 0.4344\text{ mm}$, Rainy-Day $\text{MAE} = 2.8947\text{ mm}$ (16.2% error reduction vs Persistence).
- **Target C (Rain Binary)**: $\text{Accuracy} = 89.19\%$, $\text{ROC-AUC} = 0.8366$, $\text{PR-AUC} = 0.4476$, $\text{Brier Score} = 0.0768$, $\text{ECE} = 0.0608$.

### 1.5 Strengths
1. **Sub-millisecond Inference**: Inference executes in $<0.4\text{ ms}$ per station on standard CPU, allowing real-time multi-station generation.
2. **Transparent Explainability**: Fully inspectable via exact TreeSHAP values natively supported by the booster.
3. **Discriminative Power**: Highest validation ROC-AUC ($0.9193$ in Fold 2) and PR-AUC ($0.9076$) for rain classification.
4. **Operational Robustness**: Zero PyTorch / CUDA runtime dependency required in production serving.

### 1.6 Weaknesses & Limitations
1. **Extreme Heavy Rainfall Underprediction**: Due to extreme zero-inflation ($>89\%$ dry days in winter), regression models trained with MSE/log1p smooth out extreme convective downpours ($>64.5\text{ mm}$), underpredicting maximum peaks.
2. **Tabular Horizon Limit**: Lacks explicit recurrent hidden-state memory; dynamic historical context is constrained to the engineered 7-day rolling window.

---

## 2. Model Card: PyTorch LSTM Sequence Benchmark

### 2.1 Model Details
- **Model Family**: 2-layer Recurrent Long Short-Term Memory Network with Dropout ($p=0.2$)
- **Artifacts**: `phase3_models/lstm/{target}/lstm_{target}_fold2.pt`
- **Preprocessor**: RobustScaler `phase3_models/preprocessors/scaler_lstm_{target}_fold2.joblib`
- **Sequence Length**: 7 consecutive daily steps ($T=7$)
- **Status**: `BENCHMARKED`

### 2.2 Performance Summary
- **Temperature Holdout**: $\text{MAE} = 0.6441^\circ\text{C}$, $R^2 = 0.9713$ (**Best Overall Holdout Temperature**).
- **Rainfall Holdout**: Rainy-Day $\text{MAE} = 2.8630\text{ mm}$ (**Best Active Precipitation Tracking**).
- **Rain Binary Holdout**: $\text{Accuracy} = 88.32\%$, $\text{ROC-AUC} = 0.8256$.

### 2.3 Strengths & Limitations
- **Strength**: Dynamic temporal sequence modeling excels at capturing multi-day synoptic transitions (e.g. western disturbances, sustained temperature drops).
- **Limitation**: Black-box nature lacks native exact TreeSHAP attribution; training requires $>500\text{ seconds}$ per fold (vs $30-50\text{s}$ for XGBoost); sequence preprocessing requires complete 7-day uninterrupted historical buffers per station.

---

## 3. Scientific Limitations & Ethical Disclaimers

> [!WARNING]
> 1. **Probabilistic Uncertainty**: Weather is an inherently chaotic, non-linear physical system. Model predictions are statistical estimates conditioned on historical sensor telemetry and must never be treated as deterministic guarantees.
> 2. **Dry-Season Holdout Imbalance**: The 2025 holdout period (`2025-01-01` to `2025-02-10`) reflects dry winter climatology across northern and central India ($10.4\%$ rain incidence). Verification across southwest monsoon seasons remains anchored in validation Folds 1 and 2.
> 3. **Non-Causal Attribution**: SHAP values quantify empirical model sensitivity, not physical causation. A high positive SHAP attribution for `avg_temp_clean` signifies statistical correlation with the next-day forecast, not an atmospheric cause.
