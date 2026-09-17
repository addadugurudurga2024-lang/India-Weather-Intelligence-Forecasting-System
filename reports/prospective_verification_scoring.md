# PROSPECTIVE VERIFICATION & BENCHMARK SCORING LEDGER

**Forecast Origin:** `2026-09-13`  
**Verification Engine Version:** `v1.0.0 (Audited & Hardened)`  
**Station:** New Delhi Safdarjung (`28.5833°N, 77.2000°E`)  

---

## Prospective Ground Truth Verification Strategy

In accordance with Scientific Principle #5 and #12:
- **Ground-Truth Reference:** Physical station observation recorded on date $T$ after 24-hour accumulation.
- **Zero Leaking:** Actual observation $Y_t$ is strictly isolated until time $t > T$.
- **Missing Policy:** If station telemetry is missing on date $T$, it is recorded as `UNAVAILABLE` and excluded from error computation; it is **NEVER** filled with 0.0.

## Horizon Scoring Schema & Verification Schedule

| Horizon | Target Date | Verification Eligible Date | Our Model Status | External Benchmark Status | Actual Observation Status |
|:---:|:---:|:---:|:---:|:---:|:---:|
| T+1 | `2026-09-14` | `2026-09-14 23:59 IST` | Locked & Frozen | Locked & Frozen | Pending Elapsed Observation |
| T+2 | `2026-09-15` | `2026-09-15 23:59 IST` | Locked & Frozen | Locked & Frozen | Pending Elapsed Observation |
| T+3 | `2026-09-16` | `2026-09-16 23:59 IST` | Locked & Frozen | Locked & Frozen | Pending Elapsed Observation |
| T+4 | `2026-09-17` | `2026-09-17 23:59 IST` | Locked & Frozen | Locked & Frozen | Pending Elapsed Observation |
| T+5 | `2026-09-18` | `2026-09-18 23:59 IST` | Locked & Frozen | Locked & Frozen | Pending Elapsed Observation |
| T+6 | `2026-09-19` | `2026-09-19 23:59 IST` | Locked & Frozen | Locked & Frozen | Pending Elapsed Observation |
| T+7 | `2026-09-20` | `2026-09-20 23:59 IST` | Locked & Frozen | Locked & Frozen | Pending Elapsed Observation |
| T+8 | `2026-09-21` | `2026-09-21 23:59 IST` | Locked & Frozen | Locked & Frozen | Pending Elapsed Observation |
| T+9 | `2026-09-22` | `2026-09-22 23:59 IST` | Locked & Frozen | Locked & Frozen | Pending Elapsed Observation |
| T+10 | `2026-09-23` | `2026-09-23 23:59 IST` | Locked & Frozen | Locked & Frozen | Pending Elapsed Observation |
| T+11 | `2026-09-24` | `2026-09-24 23:59 IST` | Locked & Frozen | Locked & Frozen | Pending Elapsed Observation |
| T+12 | `2026-09-25` | `2026-09-25 23:59 IST` | Locked & Frozen | Locked & Frozen | Pending Elapsed Observation |

---

## Prospective Metrics Protocol

When observations are ingested, the scoring pipeline executes:
1. **Continuous Temperature:** $\text{MAE} = \frac{1}{N} \sum |\hat{T} - T_{obs}|$, $\text{RMSE}$, $\text{Bias}$, and Empirical $80\%$ Coverage: $\mathbb{I}[\hat{T}_{p10} \le T_{obs} \le \hat{T}_{p90}]$.
2. **Rain Probability (Calibrated):** Brier Score $\text{BS} = \frac{1}{N} \sum (p_{rain} - y_{binary})^2$, Reliability Curve across probability bins $[0.0, 0.1), [0.1, 0.2), \dots$.
3. **Rainfall Depth:** $\text{MAE}$ on all days and conditional rainy-day $\text{MAE}$ ($T_{obs} > 0.1$ mm).
4. **Benchmarking:** Side-by-side relative skill comparison between our XGBoost direct multi-horizon models and Open-Meteo GFS/ECMWF numerical blend.

---

**Status:** Prospective verification pipeline is fully instantiated, deterministic, and ready to ingest physical ground truth.