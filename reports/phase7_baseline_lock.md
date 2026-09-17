# Phase 7 Baseline Cryptographic Lock & State Audit

**Project**: India Weather Forecasting & Intelligence System  
**Document**: Phase 7 Baseline Lock (Task 2)  
**Date**: 2026-09-13  
**Status**: BASELINE FROZEN  

---

## 1. Cryptographic Hashes of Phase 7 Baseline Artifacts

The following table records the exact SHA-256 signatures of all authoritative Phase 7 files prior to the audit and hardening pass. These signatures serve as the baseline comparator:

| Relpath | SHA-256 Hash | Size (Bytes) | Role |
| :--- | :--- | :---: | :--- |
| `phase7_forecasting/data/phase7_multi_horizon_evaluation_summary.json` | `3986b67be17532dabb492d1f3923efde2650805e4404aceb3dc5b284d44a8de6` | 28,839 | Multi-horizon validation benchmarks ($T+1 \dots T+12$) |
| `phase7_forecasting/data/authoritative25DayTimeline.json` | `adc75f6dd9d1651db82984d4f9c5ed6808e7f1bd45836bb06589e19193b502b4` | 368,883 | Precomputed 25-day operational seed |
| `frontend/src/data/authoritativeMultiHorizonSummary.json` | `3986b67be17532dabb492d1f3923efde2650805e4404aceb3dc5b284d44a8de6` | 28,839 | Frontend client copy |
| `frontend/src/data/authoritative25DayTimeline.json` | `adc75f6dd9d1651db82984d4f9c5ed6808e7f1bd45836bb06589e19193b502b4` | 368,883 | Frontend client copy |
| `phase7_forecasting/scripts/run_phase7_multi_horizon_engine.py` | `a125276de948f8c9760f105249babdc22eca54f18aa90169ad287f844836f552` | 22,748 | Validation engine script |
| `phase7_forecasting/scripts/operational_ingestion_service.py` | `e5fa385df209a4a94c6291a069db4b449dbff8f7dc32d6a74f7ff2bb5b54cff8` | 14,618 | Ingestion & timeline service |
| `phase7_forecasting/scripts/generate_25day_timeline_snapshots.py` | `4be54f20a76f588c1ebea7b9e597f6d93575b0b2d4c3a2436dee4037a44cd74c` | 3,253 | Snapshot generator |
| `tests/test_phase7_multi_horizon_and_operational_timeline.py` | `43e939673fb57fb93ba1a4795c42e53c98e094ffcf5d17f51c1210036dc7b65f` | 8,870 | Test suite |

---

## 2. Baseline Model Weights & Registries
- XGBoost direct models: `phase7_forecasting/models/xgb_temp_h{1,3,7,12}.json` and `xgb_rain_cls_h{1,3,7,12}.json`.
- Historical raw data: `D:\Downloads\india_weather_rainfall_data.xlsx` (`e6a636777430f078b4d970f9f46e79efcece7f97b67dd186c30a755d2783cd84`).
- Phase 3 baseline integrity lock (`phase6_evaluation/manifests/phase3_baseline_integrity_lock.json`) remains unperturbed.
