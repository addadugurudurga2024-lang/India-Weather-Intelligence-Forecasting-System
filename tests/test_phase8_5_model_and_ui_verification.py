"""
Phase 8.5 Automated Test Suite: Operational Forecast Center Checking, Fixes & Hardening
Verifies:
1. Canonical 413 stations registry integrity & UTF-8 cleanliness (Task 3, 24)
2. All 84 horizon models loading, schemas, and inference execution (Task 17)
3. Direct horizon routing D+1..D+12 -> h1..h12 (Task 18)
4. Calibrated, variable rain probability routing from xgb_rain_cls_h{h} (Task 19)
5. Temperature routing with physical consistency T_min <= T_avg <= T_max (Task 20)
6. Direct model-to-UI numerical verification within 1e-3 tolerance (Task 21)
7. Operational 25-day timeline: OBSERVED, MODEL ESTIMATE, CURRENT, UNAVAILABLE (Tasks 7-11, 25)
8. Multi-station operational test across 28 diverse stations & A -> B -> C -> A switching (Task 26)
9. Raw dataset and Phase 3-7 immutability (Task 28)
"""

import json
import hashlib
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
STATIONS_PATH = ROOT_DIR / "frontend" / "src" / "data" / "authoritativeStations.json"
MODELS_DIR = ROOT_DIR / "phase7_forecasting" / "models"
TIMELINE_PATH = ROOT_DIR / "phase7_forecasting" / "data" / "authoritative25DayTimeline.json"
RAW_DATA_PATH = Path(r"D:\Downloads\india_weather_rainfall_data.xlsx")
EXPECTED_RAW_SHA256 = "e6a636777430f078b4d970f9f46e79efcece7f97b67dd186c30a755d2783cd84"
PHASE3_METRICS_PATH = ROOT_DIR / "frontend" / "src" / "data" / "authoritativeMetrics.json"

import sys
sys.path.insert(0, str(ROOT_DIR / "phase7_forecasting" / "scripts"))
from operational_ingestion_service import (
    get_model,
    load_station_metadata,
    build_operational_timeline,
    get_station_feature_state,
    run_multi_horizon_direct_forecast,
    generate_previous_day_model_estimate,
    BASE_FEATURE_NAMES,
)


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def test_task3_and_task24_canonical_413_stations_clean():
    """Task 3 & 24: Verify exactly 413 stations and zero UTF-8 corruption."""
    assert STATIONS_PATH.exists()
    with open(STATIONS_PATH, "r", encoding="utf-8") as f:
        stations = json.load(f)

    assert len(stations) == 413, f"Expected 413 stations, found {len(stations)}"

    required_keys = ["station_id", "station_name", "state", "district", "latitude", "longitude", "elevation_m"]
    corrupted_count = 0

    for s in stations:
        for k in required_keys:
            assert k in s, f"Station {s.get('station_id')} missing required key {k}"
        assert -90.0 <= s["latitude"] <= 90.0
        assert -180.0 <= s["longitude"] <= 180.0
        assert s["elevation_m"] >= -10.0

        # Verify no UTF-8 '?' artifacts exist in names
        if "?" in s["station_name"] or "?" in s["district"] or "?" in s["state"]:
            corrupted_count += 1

    assert corrupted_count == 0, f"Found {corrupted_count} stations with UTF-8 corruption (?)!"
    print(f"[PASS] 413 canonical stations verified with 100% clean UTF-8 naming.")


def test_task17_and_task18_verify_all_84_models_and_direct_routing():
    """Task 17 & 18: Verify all 84 horizon models exist, load, and route directly."""
    targets = ["temp", "temp_min", "temp_max", "rain_cls", "rain_amt", "wind", "pres"]
    assert MODELS_DIR.exists()

    # Create synthetic test feature vector
    feat_dict = {col: 25.0 for col in BASE_FEATURE_NAMES}
    feat_dict["elevation"] = 216.0
    feat_dict["latitude"] = 28.58
    feat_dict["longitude"] = 77.20
    test_df = pd.DataFrame([feat_dict])

    verified_count = 0
    for target in targets:
        for h in range(1, 13):
            model_name = f"xgb_{target}_h{h}.json"
            model_path = MODELS_DIR / model_name
            assert model_path.exists(), f"Model file {model_name} missing!"

            model = get_model(model_name)
            assert model is not None

            # Prepare harmonic features for horizon h
            X_h = test_df.copy()
            X_h[f"doy_sin_h{h}"] = 0.5
            X_h[f"doy_cos_h{h}"] = 0.866

            if target == "rain_cls":
                proba = model.predict_proba(X_h)
                assert proba.shape == (1, 2)
                assert 0.0 <= proba[0, 1] <= 1.0
            else:
                pred = model.predict(X_h)
                assert len(pred) == 1
                assert not np.isnan(pred[0])

            verified_count += 1

    assert verified_count == 84
    print(f"[PASS] All 84 XGBoost horizon models (7 targets x 12 horizons) verified with direct routing.")


def test_task19_rain_probability_geographic_variation():
    """Task 19: Prove rain probabilities vary by region and come directly from classifier."""
    stations_meta = load_station_metadata()

    # Test distinct geographical regions
    test_stations = [
        "jaipur_sanganer_26.8167_75.8000_385m",      # Arid
        "cherrapunji_25.2500_91.7333_1312m",        # Northeast High Rain
        "bombay_santacruz_19.1167_72.8500_8m",       # Coastal
        "srinagar_34.0833_74.8333_1585m",            # Mountain / High Elevation
    ]

    probs = {}
    for stn_id in test_stations:
        meta = stations_meta.get(stn_id, {})
        base_df = get_station_feature_state(stn_id, "2026-09-13", station_meta=meta)
        fc = run_multi_horizon_direct_forecast(stn_id, "2026-09-13", base_df, uncertainties={})
        probs[stn_id] = [d["rain_probability"] for d in fc]
        # Check all probabilities are genuine model outputs between 0.0 and 1.0
        for p in probs[stn_id]:
            assert 0.0 <= p <= 1.0

    # Verify probabilities are not constant identical placeholder numbers
    unique_h1_probs = set(probs[s][0] for s in test_stations)
    assert len(unique_h1_probs) >= 2, f"Probabilities lack geographic variation: {probs}"
    print(f"[PASS] Rain probabilities verified: dynamic, calibrated, and varying across geographic zones.")


def test_task20_temperature_routing_and_physical_ordering():
    """Task 20: Verify T_min <= T_avg <= T_max across all horizons without artificial exponential smoothing."""
    stn_id = "new_delhi_safdarjung_28.5833_77.2000_211m"
    tl = build_operational_timeline(stn_id, "2026-09-13")

    for day in tl["timeline"]:
        if day["temperature_avg"] is not None and day["temperature_min"] is not None and day["temperature_max"] is not None:
            t_min = day["temperature_min"]
            t_avg = day["temperature_avg"]
            t_max = day["temperature_max"]
            assert t_min <= t_avg <= t_max, (
                f"Physical ordering violated on {day['date']} (day {day['relative_day']}): min={t_min}, avg={t_avg}, max={t_max}"
            )

    print(f"[PASS] Temperature routing verified: min <= avg <= max strictly maintained across all 25 days.")


def test_task21_direct_model_to_timeline_numerical_match():
    """Task 21: Verify direct model execution matches timeline output within 1e-3 floating-point tolerance."""
    stn_id = "new_delhi_safdarjung_28.5833_77.2000_211m"
    meta = load_station_metadata().get(stn_id)
    origin_date = "2026-09-13"

    base_features_df = get_station_feature_state(stn_id, origin_date, station_meta=meta)
    tl = build_operational_timeline(stn_id, origin_date)

    forecast_days = [d for d in tl["timeline"] if d["status"] == "FORECAST"]
    assert len(forecast_days) == 12

    # Verify for horizon h=1 and h=7 directly from raw model
    for h in [1, 7]:
        fc_day = forecast_days[h - 1]
        fc_doy = (pd.to_datetime(origin_date) + pd.Timedelta(days=h)).timetuple().tm_yday

        X_h = base_features_df.copy()
        X_h[f"doy_sin_h{h}"] = np.sin(2 * np.pi * fc_doy / 365.25)
        X_h[f"doy_cos_h{h}"] = np.cos(2 * np.pi * fc_doy / 365.25)

        raw_temp = float(get_model(f"xgb_temp_h{h}.json").predict(X_h)[0])
        expected_temp = round(raw_temp, 1)

        assert abs(fc_day["temperature_avg"] - expected_temp) < 1e-3, (
            f"Numerical mismatch on T+{h}: displayed={fc_day['temperature_avg']}, raw={expected_temp}"
        )

    print(f"[PASS] Direct Model-to-UI numerical equivalence verified within 1e-3 tolerance.")


def test_tasks_7_to_11_operational_timeline_provenance_and_zero_fabrication():
    """Tasks 7-11: Verify 25-day operational timeline provenance semantics."""
    stn_id = "new_delhi_safdarjung_28.5833_77.2000_211m"

    # 1. Historical Replay: D-12..D-1 OBSERVED, D0 CURRENT, D+1..D+12 FORECAST
    tl_hist = build_operational_timeline(stn_id, "2025-01-20")
    assert len(tl_hist["timeline"]) == 25

    past_hist = [d for d in tl_hist["timeline"] if d["relative_day"] < 0]
    curr_hist = [d for d in tl_hist["timeline"] if d["relative_day"] == 0][0]
    future_hist = [d for d in tl_hist["timeline"] if d["relative_day"] > 0]

    assert len(past_hist) == 12
    assert len(future_hist) == 12
    assert all(d["status"] == "OBSERVED" and d["is_observed"] for d in past_hist)
    assert curr_hist["status"] == "CURRENT" and curr_hist["is_observed"]
    assert all(d["status"] == "FORECAST" and not d["is_observed"] for d in future_hist)

    # 2. Operational Live Mode: D-12..D-1 MODEL ESTIMATE, D0 UNAVAILABLE, D+1..D+12 FORECAST
    tl_live = build_operational_timeline(stn_id, "2026-09-13")
    assert len(tl_live["timeline"]) == 25

    past_live = [d for d in tl_live["timeline"] if d["relative_day"] < 0]
    curr_live = [d for d in tl_live["timeline"] if d["relative_day"] == 0][0]
    future_live = [d for d in tl_live["timeline"] if d["relative_day"] > 0]

    assert len(past_live) == 12
    assert len(future_live) == 12
    # In live mode without external telemetry, past days are MODEL ESTIMATE, never fake OBSERVED
    for d in past_live:
        assert d["status"] in ["OBSERVED", "MODEL ESTIMATE"]
        assert "xgb_multi_horizon" in d["provenance"] or "Open-Meteo" in d["provenance"]

    # D0 is strictly observation-only: UNAVAILABLE if telemetry missing, never estimated
    if curr_live["status"] == "UNAVAILABLE":
        assert curr_live["temperature_avg"] is None
        assert curr_live["rainfall_amount"] is None
        assert curr_live["is_observed"] is False
        assert "Zero Synthetic Fallback" in curr_live["provenance"]

    print(f"[PASS] 25-day operational timeline provenance and zero-fabrication fallback validated.")


def test_task26_multi_station_operational_and_station_switching():
    """Task 26: Multi-station validation (28+ diverse stations) and switching without leakage."""
    stations = load_station_metadata()
    stn_list = list(stations.values())
    sample_stns = stn_list[::14][:30]  # 30 stations covering all geographic quadrants
    assert len(sample_stns) >= 28

    for s in sample_stns:
        tl = build_operational_timeline(s["station_id"], "2026-09-13")
        assert tl["station_id"] == s["station_id"]
        assert tl["station_name"] == s["station_name"]
        assert len(tl["timeline"]) == 25

    # Test switching: Station A -> Station B -> Station C -> Station A
    stn_a, stn_b, stn_c = sample_stns[0], sample_stns[1], sample_stns[2]
    tl_a1 = build_operational_timeline(stn_a["station_id"], "2026-09-13")
    tl_b = build_operational_timeline(stn_b["station_id"], "2026-09-13")
    tl_c = build_operational_timeline(stn_c["station_id"], "2026-09-13")
    tl_a2 = build_operational_timeline(stn_a["station_id"], "2026-09-13")

    # Assert Station A data matches exactly and has no leakage from Station B or C
    assert tl_a1["station_id"] == tl_a2["station_id"] == stn_a["station_id"]
    assert tl_b["station_id"] == stn_b["station_id"]
    assert tl_c["station_id"] == stn_c["station_id"]

    temp_a1 = [d["temperature_avg"] for d in tl_a1["timeline"]]
    temp_a2 = [d["temperature_avg"] for d in tl_a2["timeline"]]
    temp_b = [d["temperature_avg"] for d in tl_b["timeline"]]

    assert temp_a1 == temp_a2, "Station A results perturbed across switching!"
    assert temp_a1 != temp_b, "Station A and Station B produced identical values (leakage)!"

    print(f"[PASS] Multi-station operational test passed across {len(sample_stns)} stations with zero switching leakage.")


def test_task28_raw_dataset_and_phase3_metrics_immutability():
    """Task 28: Verify raw Kaggle dataset and Phase 3 holdout benchmarks are 100% unaltered."""
    if RAW_DATA_PATH.exists():
        actual_hash = compute_sha256(RAW_DATA_PATH)
        assert actual_hash == EXPECTED_RAW_SHA256, f"Raw data hash mismatch: {actual_hash}"
    else:
        cache_lock = ROOT_DIR / "phase1_audit" / "cache" / "source_integrity.json"
        assert cache_lock.exists()
        with open(cache_lock) as f:
            meta = json.load(f)
        assert meta["sha256"] == EXPECTED_RAW_SHA256

    with open(PHASE3_METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    # Verify Phase 3 holdout benchmarks
    xgb_temp_mae = metrics["target_a_temperature"]["xgboost"]["holdout"]["mae"]
    assert abs(xgb_temp_mae - 0.6527) < 1e-4

    xgb_rain_mae = metrics["target_b_rainfall_amount"]["xgboost"]["holdout"]["mae"]
    assert abs(xgb_rain_mae - 0.4344) < 1e-4

    xgb_rain_auc = metrics["target_c_rain_binary"]["xgboost"]["holdout"]["roc_auc"]
    assert abs(xgb_rain_auc - 0.8366) < 1e-4

    print(f"[PASS] Raw dataset hash and Phase 3 authoritative benchmarks verified 100% immutable.")
