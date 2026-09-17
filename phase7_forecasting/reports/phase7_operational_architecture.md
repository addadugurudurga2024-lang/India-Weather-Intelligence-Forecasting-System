# Phase 7 — Operational Forecasting Architecture Specification

**Project**: India Weather Forecasting & Intelligence System  
**Phase**: PHASE 7 — Operational 25-Day Weather Timeline + 12-Day Multi-Horizon Forecasting  
**Authoritative Date**: 2026-09-13  
**Status**: APPROVED ARCHITECTURE SPECIFICATION  

---

## 1. High-Level Architectural Vision

Phase 7 upgrades the forecasting platform from single-step next-day prediction ($t+1$) into an operational 25-day chronological weather timeline:
$$\underbrace{D-12 \to D-11 \to \dots \to D-1}_{\text{12 Days Actual Historical Observations}} \quad\longrightarrow\quad \underbrace{D0}_{\text{Today / Current Observed Conditions}} \quad\longrightarrow\quad \underbrace{D+1 \to D+2 \to \dots \to D+12}_{\text{12 Days Multi-Horizon Model Forecasts}}$$

The architecture is split into two rigorously separated pipelines:
1. **The Historical Validation Pipeline**: Offline, strictly chronological, walk-forward training, tuning, and benchmarking on immutable historical canonical datasets (2021–2025), preserving isolated holdouts and baseline locks.
2. **The Operational Forecast Pipeline**: Online/inference-time ingestion of actual current observations at forecast origin $D0$, forward evaluation through calibrated multi-horizon models, uncertainty quantification, and assembly of the unified 25-day data contract with full provenance.

```
+---------------------------------------------------------------------------------------------------+
|                                1. HISTORICAL VALIDATION PIPELINE                                  |
|                                                                                                   |
|  [Canonical Historical Dataset]                                                                   |
|   (413 Stations, 2021-2025)                                                                       |
|                |                                                                                  |
|                v                                                                                  |
|  [Multi-Horizon Target Engineering] -> target_{var}_h{1..12} (t+1 ... t+12)                       |
|                |                                                                                  |
|                v                                                                                  |
|  [Feature Availability Matrix] ------> Strict prevention of future leakage                        |
|                |                       (Only X_t + deterministic cyclical harmonics at t+h)        |
|                v                                                                                  |
|  [Chronological Walk-Forward] -------> Fold 1 (2021-2022 -> 2023)                                 |
|                |                       Fold 2 (2021-2023 -> 2024)                                 |
|                v                                                                                  |
|  [Model Benchmarking Engine] --------> Persistence vs Climatology vs Direct XGB vs PyTorch LSTM  |
|                |                                                                                  |
|                v                                                                                  |
|  [Uncertainty & Calibration Engine] -> Empirical Quantile Residuals [P10, P50, P90] + 10-bin ECE   |
|                |                                                                                  |
|                v                                                                                  |
|  [Isolated 2025 Holdout Gate] -------> Standing at D0 in unseen out-of-time evaluation            |
+---------------------------------------------------------------------------------------------------+
                                                 |
                                                 v
+---------------------------------------------------------------------------------------------------+
|                                 2. OPERATIONAL FORECAST PIPELINE                                  |
|                                                                                                   |
|  [Forecast Origin Request: D0, station_id]                                                        |
|                |                                                                                  |
|                +------------------------------------+                                             |
|                |                                    |                                             |
|                v                                    v                                             |
|  [D-12 ... D-1 Actual Observations]   [D0 Current Conditions Observation]                         |
|  - Historical Archive / Canonical IMD - Real-time Ingestion (Open-Meteo CC BY 4.0 / WMO)          |
|  - Status: "OBSERVED"                 - Status: "CURRENT"                                         |
|  - If unavailable: null / "UNAVAILABLE"- If unavailable: null / "UNAVAILABLE"                     |
|                |                                    |                                             |
|                +-----------------+------------------+                                             |
|                                  |                                                                |
|                                  v                                                                |
|                     [Current Feature Vector: X_0]                                                 |
|                                  |                                                                |
|                                  v                                                                |
|                     [Multi-Horizon Model Ingestion]                                               |
|                     (Direct Horizon-Specific Models f_1 ... f_12)                                 |
|                                  |                                                                |
|                                  v                                                                |
|                     [D+1 ... D+12 Predictions]                                                    |
|                     - Point Forecasts (Avg/Min/Max Temp, Rain Amt, Rain Prob, Wind, Pressure)     |
|                     - Uncertainty Bands (80% & 95% Empirical Prediction Intervals)                |
|                     - Status: "FORECAST"                                                          |
|                                  |                                                                |
|                                  v                                                                |
|                     [Unified 25-Day Schema Assembly]                                              |
|                     (Full Provenance, Model IDs, Uncertainty Metadata)                            |
|                                  |                                                                |
|                                  v                                                                |
|                     [React + TypeScript Forecast Center]                                          |
|                     (Interactive 25-Day Strip, D0 Panel, Skill Degradation Charts)                |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Core Separation of Concerns

### 2.1 The Two Inviolable Tenets
1. **Never Confuse History, Current, and Forecast**:
   - An observation that occurred in the past is `OBSERVED`.
   - The measurement taken on the current operational day is `CURRENT`.
   - A model projection for tomorrow or day 12 is `FORECAST`.
   - A calculated statistic (e.g. 7-day rolling mean) is `DERIVED`.
   - Any missing sensor or unreachable telemetry is `UNAVAILABLE`.
2. **Zero Synthetic Imputation at Runtime**:
   - If an observation cannot be fetched from authoritative telemetry, the system outputs `null` and sets the status to `"UNAVAILABLE"`.
   - Under no circumstances will the system execute model inference to backfill historical days and pass them off as "recorded data".

---

## 3. Mathematical Formulation of Multi-Horizon Forecasting

Given a panel of weather time series observed across $N=413$ stations at daily time steps $t \in \{1, \dots, T\}$:
$$X_t = \left[ x_{t,1}, x_{t,2}, \dots, x_{t,K} \right] \in \mathbb{R}^K$$
where $K=26$ represents the feature set engineered in Phase 3.

For each forecast horizon $h \in \{1, 2, \dots, 12\}$, we aim to predict target variable $y_{t+h}$ using **only information available at or before time $t$**:
$$\hat{y}_{t+h} = f_h(X_t, Z_{t+h})$$
where:
- $X_t$ contains strictly observed features up to time $t$ (thermal lags, rainfall sums, barometric trends).
- $Z_{t+h}$ contains strictly deterministic, non-leaking astronomical calendar features at time $t+h$ (day-of-year harmonic $\sin(2\pi \cdot \text{doy}/365.25)$, $\cos(2\pi \cdot \text{doy}/365.25)$).
- **Leakage Prevention Axiom**: Under no circumstances can $X_{t+1} \dots X_{t+h-1}$ be used as input features to $f_h$.

---

## 4. Modeling Strategy: Direct Horizon-Specific vs. Recursive Autoregression

| Criterion | Direct Horizon-Specific ($f_h(X_t)$) | Recursive Autoregressive ($f_1(\hat{X}_{t+k-1})$) |
| :--- | :--- | :--- |
| **Error Propagation** | **Zero compounding**: Errors at $h=1$ do not distort predictions at $h=12$. | **Exponential compounding**: Small biases in early steps compound rapidly. |
| **Feature Dependencies** | Uses only real measurements observed at $t$. | Depends on noisy model predictions feeding into nonlinear lag functions. |
| **Target Loss Alignment** | Optimizes $\min \sum (y_{t+h} - f_h(X_t))^2$ directly for each horizon $h$. | Only optimizes for next-day 1-step loss $\min \sum (y_{t+1} - f(X_t))^2$. |
| **Inference Latency** | Parallel or single batch inference ($<2\text{ ms}$ for 12 horizons). | Sequential 12-step loop requiring repeated feature recalculation. |
| **Decision** | **SELECTED AS PRIMARY PRODUCTION STRATEGY** | Benchmarked as comparison baseline. |

---

## 5. Summary

This specification guarantees mathematical integrity, eliminates temporal data leakage, and provides clear architectural contracts connecting raw station telemetry, calibrated gradient boosted models, and the React 25-day interactive UI.
