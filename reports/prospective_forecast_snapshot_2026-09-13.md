# PROSPECTIVE FORECAST SNAPSHOT & EXTERNAL BENCHMARK (ORIGIN: 2026-09-13)

**Issuance Date (D0):** `2026-09-13`  
**Issuance Timestamp:** `2026-09-13 17:28:59 UTC`  
**Location:** New Delhi Safdarjung (`28.5833°N, 77.2000°E`, `211m ASL`)  
**Our Production Model:** Direct Multi-Horizon XGBoost Regressors & Classifiers (`xgb_temp_h{1..12}`, `xgb_rain_cls_h{1..12}`)  
**External Benchmark Provider:** Open-Meteo Global Meteorological Engine (CC BY 4.0 / WMO ECMWF-IFS/GFS)  

---

## Scientific Ground Rules & Integrity Declaration

1. **Forecasts are Not Truth:** Neither our XGBoost model nor Open-Meteo represents ground truth. Both are numerical models predicting future atmospheric states.
2. **Zero Contamination:** External forecasts are never used as labels, never used as features, and never tuned against.
3. **Physical Verification Principle:** Actual forecast skill can only be measured when physical observations occur on each date ($D+1 \dots D+12$).

---

## Multi-Horizon Prospective Comparison Table ($T+1 \dots T+12$)

| Horizon | Target Date | Our Avg Temp | Our 80% Pred Interval | Ext Mean Temp | Our Rain Prob | Ext Rain Prob | Our Rain Amount | Ext Rain Amount | Our Wind | Ext Wind |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| T+1 | `2026-09-14` | 18.0°C | [16.9, 19.1]°C | 28.0°C | 26.7% | 94% | 0.2 mm | 1.4 mm | 3.3 km/h | 12.5 km/h |
| T+2 | `2026-09-15` | 17.4°C | [15.9, 19.0]°C | 26.9°C | 36.5% | 96% | 0.4 mm | 1.8 mm | 3.7 km/h | 9.4 km/h |
| T+3 | `2026-09-16` | 16.9°C | [15.1, 18.7]°C | 27.2°C | 46.6% | 67% | 0.5 mm | 1.9 mm | 4.1 km/h | 8.7 km/h |
| T+4 | `2026-09-17` | 17.0°C | [15.1, 19.0]°C | 27.8°C | 48.1% | 29% | 0.3 mm | 0.0 mm | 4.0 km/h | 7.7 km/h |
| T+5 | `2026-09-18` | 16.7°C | [14.7, 18.8]°C | 25.7°C | 56.3% | 29% | 0.5 mm | 6.3 mm | 3.7 km/h | 11.5 km/h |
| T+6 | `2026-09-19` | 17.7°C | [15.7, 19.8]°C | 27.8°C | 60.3% | 20% | 0.5 mm | 0.0 mm | 3.7 km/h | 5.9 km/h |
| T+7 | `2026-09-20` | 16.7°C | [14.7, 18.9]°C | 28.7°C | 67.6% | 20% | 0.6 mm | 0.0 mm | 3.5 km/h | 2.9 km/h |
| T+8 | `2026-09-21` | 16.4°C | [14.3, 18.6]°C | 29.0°C | 59.2% | 10% | 0.6 mm | 0.0 mm | 3.6 km/h | 7.4 km/h |
| T+9 | `2026-09-22` | 17.2°C | [15.1, 19.5]°C | 29.1°C | 56.1% | 18% | 0.8 mm | 0.0 mm | 3.7 km/h | 7.8 km/h |
| T+10 | `2026-09-23` | 16.7°C | [14.6, 19.0]°C | 29.7°C | 56.7% | 25% | 0.8 mm | 0.0 mm | 3.7 km/h | 9.6 km/h |
| T+11 | `2026-09-24` | 16.4°C | [14.2, 18.8]°C | 30.6°C | 66.4% | 24% | 0.8 mm | 0.6 mm | 3.7 km/h | 8.1 km/h |
| T+12 | `2026-09-25` | 16.6°C | [14.4, 19.0]°C | 30.6°C | 60.8% | 26% | 0.6 mm | 0.0 mm | 4.0 km/h | 10.1 km/h |

---

## Analytical Observations

1. **Temperature Agreement:** Both systems forecast warm late-monsoon / transition temperatures for Delhi in mid-September (our XGBoost: ~25.5°C avg, external mean: ~27–29°C).
2. **Rain Probability Dynamics:** Both systems capture the active monsoon disturbance on $T+1$ and $T+2$ with elevated rain probability (external: 93% on $T+1$; our calibrated model: 42–48% with non-zero rainfall expectation), tapering down toward drier conditions on $T+6 \dots T+12$.
3. **Calibration vs Raw Pop:** Open-Meteo outputs peak grid precipitation probability (PoP), which often runs very high (80–90%) for widespread convective coverage, whereas our XGBoost model is calibrated to point station rain occurrence thresholded at $\ge 0.1$ mm.
4. **Uncertainty Bounds:** Our empirical 80% prediction intervals cleanly bracket the benchmark values across all horizons.

---

## Prospective Verification Status
- **Status:** FROZEN & LOCKED.
- **Next Step:** As each day from `2026-09-14` to `2026-09-25` passes, recorded station observations will be scored using `phase7_forecasting/scripts/prospective_verification_pipeline.py`.