# Phase 6 — Meteorological Model Explainability & Attribution Report

## 1. Global TreeSHAP Feature Attributions

TreeSHAP values were computed using XGBoost's native `pred_contribs` algorithm across all 26 features engineered in Phase 3. 

### 1.1 Temperature Regressor Feature Attributions
| Rank | Feature Name | Mean Absolute SHAP ($^\circ\text{C}$) | Direction of Sensitivity | Physical Meteorological Meaning |
| :---: | :--- | :---: | :--- | :--- |
| **1** | `avg_temp_clean` | **$2.8269^\circ\text{C}$** | Positive ($\rho = +0.999$) | Current surface temperature (thermal inertia) |
| **2** | `rolling_7d_temp_mean` | **$0.4082^\circ\text{C}$** | Non-linear ($\rho \approx 0.0$) | Synoptic baseline airmass temperature |
| **3** | `rolling_3d_temp_mean` | **$0.3679^\circ\text{C}$** | Non-linear ($\rho \approx 0.0$) | Short-term thermal trend momentum |
| **4** | `lag_1_avg_temp` | **$0.2864^\circ\text{C}$** | Non-linear ($\rho \approx 0.0$) | Previous day's diurnal anchor |
| **5** | `max_temp_clean` | **$0.1278^\circ\text{C}$** | Non-linear ($\rho \approx 0.0$) | Peak daytime solar heating |
| **6** | `min_temp_clean` | **$0.0984^\circ\text{C}$** | Positive ($\rho = +0.654$) | Radiative cooling floor |
| **7** | `doy_cos` | **$0.0712^\circ\text{C}$** | Negative ($\rho = -0.842$) | Annual solar declination cycle |
| **8** | `air_pressure` | **$0.0543^\circ\text{C}$** | Negative ($\rho = -0.312$) | Barometric high/low pressure systems |
| **9** | `elevation` | **$0.0489^\circ\text{C}$** | Negative ($\rho = -0.420$) | Adiabatic lapse rate altitude cooling |
| **10**| `latitude` | **$0.0381^\circ\text{C}$** | Negative ($\rho = -0.510$) | Meridional insolation gradient |

### 1.2 Rain Classifier Feature Attributions
| Rank | Feature Name | Mean Absolute SHAP (log-odds) | Direction of Sensitivity | Physical Meteorological Meaning |
| :---: | :--- | :---: | :--- | :--- |
| **1** | `rainfall` | **$1.0207$** | Non-linear | Active precipitation presence |
| **2** | `min_temp_clean` | **$0.4444$** | Positive ($\rho = +0.919$) | Nocturnal cloud insulation / humidity trap |
| **3** | `doy_cos` | **$0.4313$** | Negative ($\rho = -0.929$) | Seasonal monsoon vs dry cycle |
| **4** | `avg_temp_clean` | **$0.3737$** | Negative ($\rho = -0.646$) | Relative atmospheric stability |
| **5** | `lag_1_rainfall` | **$0.2781$** | Non-linear | Multi-day persistent synoptic system |
| **6** | `rolling_3d_rainfall_sum` | **$0.2415$** | Non-linear | Cumulative ground saturation |
| **7** | `air_pressure` | **$0.1892$** | Negative ($\rho = -0.421$) | Cyclonic low pressure / depression |
| **8** | `rolling_7d_rainfall_sum` | **$0.1542$** | Non-linear | Weekly monsoon trough activity |
| **9** | `wind_speed` | **$0.0981$** | Positive ($\rho = +0.312$) | Advective moisture transport |
| **10**| `elevation` | **$0.0682$** | Positive ($\rho = +0.241$) | Orographic precipitation enhancement |

---

## 2. Calibration & Decision Threshold Diagnostics

### 2.1 Expected Calibration Error (ECE)
- **Holdout ECE**: $0.0608$ ($6.08\%$).
- **Brier Score Loss**: $0.0807$.
- **Interpretation**: Predicted rain probabilities show strong fidelity to empirical precipitation frequencies. Stations assigned a $70\%$ probability experience rain $\sim 68.4\%$ of the time.

### 2.2 Threshold Optimization
- At the standard decision boundary $\tau = 0.50$:
  - Precision: $47.7\%$, Recall: $39.7\%$, F1-Score: $0.4330$.
- At the F1-optimal decision boundary $\tau = 0.30$:
  - Precision: $38.4\%$, Recall: $54.1\%$, F1-Score: **$0.4493$** ($+3.8\%$ relative F1 gain).
- *Finding*: For operational warnings where false negatives (unwarned rain) carry higher risk than false alarms, an operating threshold of $\tau = 0.30-0.35$ provides superior sensitivity.

---

## 3. Sequence Modeling Attribution & LSTM Limitations

### 3.1 Input Dynamics
PyTorch LSTM processes a $T=7$ daily rolling window across 26 normalized features. Its hidden state vector ($H \in \mathbb{R}^{64}$) continuously tracks temporal momentum, which explains its superior performance on abrupt cold-front arrivals and active monsoon days.

### 3.2 Interpretable Attribution Limitations
Unlike tree-based models where path traversals yield mathematically exact local Shapley values, standard 2-layer LSTMs with tanh/sigmoid recurrent activations lack closed-form additive local explanations. Gradient-based attributions on recurrent inputs can fluctuate significantly due to vanishing gradients across early sequence steps. Therefore, the LSTM is documented as an effective sequence benchmark with lower inherent interpretability than XGBoost.
