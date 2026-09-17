# Phase 6 — Comprehensive Model Benchmark Report

## 1. Executive Benchmarking Matrix

| Modeling Target | Evaluation Period | Persistence / Majority Baseline | XGBoost Tabular GBDT | PyTorch LSTM (7-Day Sequence) | Winning Architecture |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Target A: Temperature** | 2025 Holdout | $\text{MAE} = 0.7235^\circ\text{C}$ ($R^2 = 0.9635$) | $\text{MAE} = 0.6527^\circ\text{C}$ ($R^2 = 0.9705$) | $\mathbf{MAE = 0.6441^\circ C}$ ($\mathbf{R^2 = 0.9713}$) | **LSTM** (Holdout) / **XGBoost** (Speed) |
| **Target A: Temperature** | Fold 2 (2024) | $\text{MAE} = 0.7185^\circ\text{C}$ | $\mathbf{MAE = 0.7015^\circ C}$ ($R^2 = 0.9693$) | $\text{MAE} = 0.7115^\circ\text{C}$ ($R^2 = 0.9673$) | **XGBoost** |
| **Target A: Temperature** | Fold 1 (2023) | $\text{MAE} = 0.7298^\circ\text{C}$ | $\mathbf{MAE = 0.7161^\circ C}$ ($R^2 = 0.9621$) | $\text{MAE} = 0.7854^\circ\text{C}$ ($R^2 = 0.9568$) | **XGBoost** |
| **Target B: Rainfall Amount**| 2025 Holdout Overall | $\text{MAE} = 0.5026\text{ mm}$ | $\mathbf{MAE = 0.4344\text{ mm}}$ | $\text{MAE} = 0.4368\text{ mm}$ | **XGBoost** |
| **Target B: Rainfall Amount**| 2025 Holdout Rainy Only | $\text{MAE} = 3.4563\text{ mm}$ | $\text{MAE} = 2.8947\text{ mm}$ | $\mathbf{MAE = 2.8630\text{ mm}}$ | **LSTM** |
| **Target B: Rainfall Amount**| Fold 2 (2024) Overall | $\text{MAE} = 4.2735\text{ mm}$ | $\mathbf{MAE = 3.3739\text{ mm}}$ | $\text{MAE} = 3.3873\text{ mm}$ | **XGBoost** |
| **Target B: Rainfall Amount**| Fold 2 (2024) Rainy Only| $\text{MAE} = 8.6904\text{ mm}$ | $\text{MAE} = 7.1290\text{ mm}$ | $\mathbf{MAE = 7.0867\text{ mm}}$ | **LSTM** |
| **Target C: Rain Binary** | 2025 Holdout | $\text{Acc} = 89.59\%$, $\text{AUC} = 0.5000$ | $\text{Acc} = 89.19\%$, $\mathbf{AUC = 0.8366}$ | $\text{Acc} = 88.32\%$, $\text{AUC} = 0.8256$ | **XGBoost** |
| **Target C: Rain Binary** | Fold 2 (2024) | $\text{Acc} = 55.78\%$, $\text{AUC} = 0.5000$ | $\mathbf{Acc = 84.76\%}$, $\mathbf{F1 = 0.8300}$, $\mathbf{AUC = 0.9193}$ | $\text{Acc} = 83.76\%$, $\text{F1} = 0.8197$, $\text{AUC} = 0.9096$ | **XGBoost** |

---

## 2. Cross-Fold Stability Analysis (Fold 1 $\rightarrow$ Fold 2)

- **Temperature Stability**:
  - XGBoost: MAE shifted from $0.7161^\circ\text{C}$ (Fold 1) to $0.7015^\circ\text{C}$ (Fold 2), a modest improvement of $-2.0\%$.
  - LSTM: MAE shifted from $0.7854^\circ\text{C}$ (Fold 1) to $0.7115^\circ\text{C}$ (Fold 2), an improvement of $-9.4\%$.
  - Both architectures demonstrated positive stability gains as the expanding training window expanded from 2 to 3 years.
- **Rainfall Stability**:
  - Fold 2 exhibited higher active monsoon rainfall across India than Fold 1, resulting in higher rainy-day MAE for all models (XGBoost: $6.49\text{ mm} \rightarrow 7.13\text{ mm}$; LSTM: $6.55\text{ mm} \rightarrow 7.09\text{ mm}$).
  - Despite the climatic shift, relative error reduction vs Persistence remained constant ($16.3\%$ in Fold 1 vs $18.0\%$ in Fold 2).

---

## 3. Holdout Generalization Analysis (2025 Winter Holdout)

- **Climatological Shift**:
  - The holdout period (`2025-01-01` to `2025-02-10`) features winter conditions with $10.4\%$ rain prevalence.
  - Overall rainfall MAE dropped dramatically ($0.4344\text{ mm}$ holdout vs $3.3739\text{ mm}$ validation) due to zero-inflation in dry winter conditions.
  - Rainy-day MAE remained highly challenging ($2.8947\text{ mm}$ holdout vs $3.4563\text{ mm}$ persistence baseline).
- **Classification Generalization**:
  - While Majority baseline accuracy reached $89.59\%$ by always predicting dry, its discrimination was trivial ($\text{ROC-AUC} = 0.5000$).
  - XGBoost maintained strong discrimination ($\text{ROC-AUC} = 0.8366$) and Brier calibration score of $0.0807$.

---

## 4. Stratified Error Slices

### 4.1 Topographic Elevation Strata
| Elevation Band | Sample Station-Days | Mean Absolute Error (Temperature) |
| :--- | :--- | :--- |
| **High Himalayan ($\ge 1500\text{ m}$)** | 273 | **$1.606^\circ\text{C}$** |
| **Sub-Himalayan / Ghats ($1000-1499\text{ m}$)** | 273 | **$1.111^\circ\text{C}$** |
| **Deccan Plateau ($600-999\text{ m}$)** | 2,752 | **$0.730^\circ\text{C}$** |
| **High Plains ($300-599\text{ m}$)** | 5,160 | **$0.669^\circ\text{C}$** |
| **Coastal / Low Plains ($<300\text{ m}$)** | 7,864 | **$0.589^\circ\text{C}$** |

*Finding*: High-altitude alpine stations ($\ge 1500\text{ m}$) experience $\sim 2.7\times$ higher temperature forecast error ($1.606^\circ\text{C}$) than low coastal plains ($0.589^\circ\text{C}$) due to extreme local lapse rates, shadow effects, and rapid snow cover shifts.

### 4.2 Rainfall Intensity Error Strata
- **Dry Days ($0.0\text{ mm}$)**: $\text{MAE} = 0.156\text{ mm}$ ($N = 14,624$).
- **Very Light ($<2.5\text{ mm}$)**: $\text{MAE} = 0.957\text{ mm}$ ($N = 811$).
- **Light ($2.5-7.5\text{ mm}$)**: $\text{MAE} = 2.451\text{ mm}$ ($N = 478$).
- **Moderate ($7.6-35.5\text{ mm}$)**: $\text{MAE} = 6.820\text{ mm}$ ($N = 345$).
- **Rather Heavy ($35.6-64.4\text{ mm}$)**: $\text{MAE} = 20.312\text{ mm}$ ($N = 54$).
- **Heavy / Torrential ($\ge 64.5\text{ mm}$)**: $\text{MAE} = 38.640\text{ mm}$ ($N = 11$).

*Finding*: Extreme convective events exhibit noticeable underprediction, an unavoidable trade-off of $\log(1+x)$ regression with Mean Squared Error loss.
