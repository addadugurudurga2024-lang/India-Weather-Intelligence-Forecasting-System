# Phase 7 — Supported Variables & Feature Availability Matrix

**Project**: India Weather Forecasting & Intelligence System  
**Phase**: PHASE 7 — Operational 25-Day Weather Timeline + 12-Day Multi-Horizon Forecasting  
**Authoritative Date**: 2026-09-13  
**Status**: APPROVED SCIENTIFIC MATRIX  

---

## 1. Supported Forecast Variables & Boundaries (Task 3)

The system supports exactly 7 target variables across $h \in \{1, 2, \dots, 12\}$ horizons:

| Variable Family | Target Name | Physical Unit | Transformation | Description |
| :--- | :--- | :---: | :---: | :--- |
| **Temperature** | `avg_temp` | $^\circ\text{C}$ | Identity (Linear) | Daily mean 2-meter air temperature |
| **Temperature** | `min_temp` | $^\circ\text{C}$ | Identity (Linear) | Daily minimum air temperature |
| **Temperature** | `max_temp` | $^\circ\text{C}$ | Identity (Linear) | Daily maximum air temperature |
| **Atmospheric** | `wind_speed` | $\text{km/h}$ | Identity (Linear) | Daily mean horizontal wind speed |
| **Atmospheric** | `air_pressure` | $\text{hPa}$ | Identity (Linear) | Daily mean barometric pressure |
| **Rainfall** | `rainfall_amount` | $\text{mm}$ | $\log(1+x)$ / Inverse $\exp(y)-1$ | Daily total precipitation accumulation |
| **Rainfall** | `rain_binary` | Binary / Prob $[0,1]$ | Sigmoid / Logistic Log-Loss | Rain occurrence indicator ($\text{rainfall} > 0\text{ mm}$) |

### Inviolable Negative Scope
1. **HUMIDITY IS STRICTLY EXCLUDED**: Humidity is absent from the canonical Kaggle dataset. It must not be synthesized, predicted, or imputed into the model feature pipeline.
2. **HOURLY FORECASTS ARE STRICTLY EXCLUDED**: Daily aggregated station records cannot support sub-daily timing ("rain starts at 3:15 PM"). All horizons operate on calendar days.
3. **WEATHER CONDITION LABELS**: Descriptive text labels (e.g. "Sunny", "Thunderstorm") are not in the raw ground truth and will not be fabricated.

---

## 2. Feature Availability Matrix for Horizons T+1 through T+12 (Task 5)

To guarantee 100% mathematical prevention of future data leakage, input features at forecast origin $t$ must adhere to strict temporal availability rules:

| Feature Name | Category | Available at Origin $t$? | Value at $t+h$ Allowed? | Justification / Leakage Safeguard |
| :--- | :---: | :---: | :---: | :--- |
| `avg_temp_clean` | Current Observation | **YES** ($t$) | **FORBIDDEN** ($t+h$) | Surface temperature measured on day $t$. Future is unobserved. |
| `min_temp_clean` | Current Observation | **YES** ($t$) | **FORBIDDEN** ($t+h$) | Daily minimum measured on day $t$. |
| `max_temp_clean` | Current Observation | **YES** ($t$) | **FORBIDDEN** ($t+h$) | Daily maximum measured on day $t$. |
| `wind_speed` | Current Observation | **YES** ($t$) | **FORBIDDEN** ($t+h$) | Wind speed measured on day $t$. |
| `air_pressure` | Current Observation | **YES** ($t$) | **FORBIDDEN** ($t+h$) | Atmospheric pressure measured on day $t$. |
| `rainfall` | Current Observation | **YES** ($t$) | **FORBIDDEN** ($t+h$) | Rainfall measured on day $t$. Missing remains `NaN` (never 0). |
| `lag_1_avg_temp` | Lagged Observation | **YES** ($t-1$) | **FORBIDDEN** | Measured temperature 24h prior to origin $t$. |
| `lag_2_avg_temp` | Lagged Observation | **YES** ($t-2$) | **FORBIDDEN** | Measured temperature 48h prior to origin $t$. |
| `lag_1_min_temp` | Lagged Observation | **YES** ($t-1$) | **FORBIDDEN** | Measured min temperature 24h prior to origin $t$. |
| `lag_1_max_temp` | Lagged Observation | **YES** ($t-1$) | **FORBIDDEN** | Measured max temperature 24h prior to origin $t$. |
| `lag_1_rainfall` | Lagged Observation | **YES** ($t-1$) | **FORBIDDEN** | Measured rainfall 24h prior to origin $t$. |
| `lag_2_rainfall` | Lagged Observation | **YES** ($t-2$) | **FORBIDDEN** | Measured rainfall 48h prior to origin $t$. |
| `lag_1_wind_speed` | Lagged Observation | **YES** ($t-1$) | **FORBIDDEN** | Measured wind speed 24h prior to origin $t$. |
| `lag_1_air_pressure` | Lagged Observation | **YES** ($t-1$) | **FORBIDDEN** | Measured air pressure 24h prior to origin $t$. |
| `rolling_3d_temp_mean` | Rolling Summary | **YES** ($[t-2, t]$) | **FORBIDDEN** | 3-day backward moving average up to origin $t$. |
| `rolling_7d_temp_mean` | Rolling Summary | **YES** ($[t-6, t]$) | **FORBIDDEN** | 7-day backward moving average up to origin $t$. |
| `rolling_7d_temp_std` | Rolling Summary | **YES** ($[t-6, t]$) | **FORBIDDEN** | 7-day backward temperature volatility up to origin $t$. |
| `rolling_3d_rainfall_sum` | Rolling Summary | **YES** ($[t-2, t]$) | **FORBIDDEN** | 3-day backward cumulative precipitation up to origin $t$. |
| `rolling_7d_rainfall_sum` | Rolling Summary | **YES** ($[t-6, t]$) | **FORBIDDEN** | 7-day backward cumulative precipitation up to origin $t$. |
| `elevation` | Static Topography | **YES** (Static) | **YES** (Static) | Physical station attribute (meters above sea level). |
| `latitude` | Static Geography | **YES** (Static) | **YES** (Static) | Physical station attribute (degrees North). |
| `longitude` | Static Geography | **YES** (Static) | **YES** (Static) | Physical station attribute (degrees East). |
| `doy_sin(t+h)` | Calendar Harmonic | **YES** (Deterministic) | **YES** (Deterministic) | $\sin(2\pi \cdot \text{doy}_{t+h} / 365.25)$. Perfectly known ahead of time. |
| `doy_cos(t+h)` | Calendar Harmonic | **YES** (Deterministic) | **YES** (Deterministic) | $\cos(2\pi \cdot \text{doy}_{t+h} / 365.25)$. Perfectly known ahead of time. |
| `month_sin(t+h)` | Calendar Harmonic | **YES** (Deterministic) | **YES** (Deterministic) | $\sin(2\pi \cdot \text{month}_{t+h} / 12.0)$. Perfectly known ahead of time. |
| `month_cos(t+h)` | Calendar Harmonic | **YES** (Deterministic) | **YES** (Deterministic) | $\cos(2\pi \cdot \text{month}_{t+h} / 12.0)$. Perfectly known ahead of time. |

---

## 3. Mathematical Proof of Zero Leakage

For any forecast origin $t_0$ and target horizon $h \in \{1, \dots, 12\}$:
$$\mathcal{I}_{t_0} = \sigma\left( \{ X_s \mid s \le t_0 \} \cup \{ Z_{s} \mid s \in \mathbb{Z} \} \right)$$
where $X_s$ is the observation filtration up to $t_0$ and $Z_s$ is the deterministic astronomical solar declination cycle.
Because $\forall k \ge 1, X_{t_0+k} \notin \mathcal{I}_{t_0}$, the model $f_h$ is strictly conditional on $\mathcal{I}_{t_0}$:
$$\mathbb{E}\left[ Y_{t_0+h} \mid \mathcal{I}_{t_0} \right] \approx f_h(X_{t_0}, Z_{t_0+h})$$
This proves that no future meteorological telemetry leaks into the feature space.
