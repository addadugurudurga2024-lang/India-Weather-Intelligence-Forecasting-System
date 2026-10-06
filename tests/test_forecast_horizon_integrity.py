"""
Test Suite: Forecast Center Horizon Differentiation & Prediction Inference Integrity Fix
Covers Tests 1 through 20 as mandated by the Final Master Prompt.
"""

import sys
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "phase7_forecasting" / "scripts"))

from phase7_forecasting.scripts.operational_ingestion_service import (
    build_operational_timeline,
    get_model,
    get_station_feature_state,
    get_horizon_inference_diagnostics,
    MODELS_DIR,
)
from backend.app.services.forecast_service import (
    get_operational_timeline,
    get_multi_horizon_forecast,
    get_current_telemetry,
    get_horizon_diagnostics,
)

TEST_STATION = "new_delhi_safdarjung_28.5833_77.2000_211m"
REPLAY_ORIGIN = "2025-01-20"


# ---------------------------------------------------------------------------
# TEST 1, 2, 3: Dedicated Horizon-Specific Models
# ---------------------------------------------------------------------------

def test_1_h1_uses_h1_model():
    """TEST 1: H1 uses h1 model."""
    m1_temp = get_model("xgb_temp_h1.json")
    m1_min = get_model("xgb_temp_min_h1.json")
    m1_max = get_model("xgb_temp_max_h1.json")
    m1_cls = get_model("xgb_rain_cls_h1.json")
    m1_amt = get_model("xgb_rain_amt_h1.json")
    m1_wind = get_model("xgb_wind_h1.json")
    m1_pres = get_model("xgb_pres_h1.json")

    assert m1_temp is not None
    assert "doy_sin_h1" in getattr(m1_temp, "feature_names_in_", [])
    assert "doy_cos_h1" in getattr(m1_temp, "feature_names_in_", [])
    assert "doy_sin_h2" not in getattr(m1_temp, "feature_names_in_", [])


def test_2_h2_uses_h2_model():
    """TEST 2: H2 uses h2 model."""
    m2_temp = get_model("xgb_temp_h2.json")
    assert m2_temp is not None
    assert "doy_sin_h2" in getattr(m2_temp, "feature_names_in_", [])
    assert "doy_cos_h2" in getattr(m2_temp, "feature_names_in_", [])
    assert "doy_sin_h1" not in getattr(m2_temp, "feature_names_in_", [])


def test_3_h12_uses_h12_model():
    """TEST 3: H12 uses h12 model."""
    m12_temp = get_model("xgb_temp_h12.json")
    assert m12_temp is not None
    assert "doy_sin_h12" in getattr(m12_temp, "feature_names_in_", [])
    assert "doy_cos_h12" in getattr(m12_temp, "feature_names_in_", [])
    assert "doy_sin_h1" not in getattr(m12_temp, "feature_names_in_", [])


# ---------------------------------------------------------------------------
# TEST 4, 5, 6: Target Date & Calendar Feature Regeneration
# ---------------------------------------------------------------------------

def test_4_target_date_increments_correctly():
    """TEST 4: Target date increments correctly from D0."""
    origin_dt = datetime.strptime(REPLAY_ORIGIN, "%Y-%m-%d")
    tl = get_operational_timeline(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)
    timeline = tl["timeline"]

    for h in range(1, 13):
        item = next(d for d in timeline if d["day_offset"] == h)
        expected_date = (origin_dt + timedelta(days=h)).strftime("%Y-%m-%d")
        assert item["date"] == expected_date, f"Horizon H{h} expected date {expected_date}, got {item['date']}"


def test_5_target_date_calendar_features_correspond():
    """TEST 5: Target-date calendar features correspond to each target date."""
    diag = get_horizon_diagnostics(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)
    origin_dt = datetime.strptime(REPLAY_ORIGIN, "%Y-%m-%d")

    for entry in diag["diagnostics"]:
        h = entry["horizon"]
        target_dt = origin_dt + timedelta(days=h)
        expected_doy = target_dt.timetuple().tm_yday
        expected_sin = round(float(np.sin(2 * np.pi * expected_doy / 365.25)), 6)
        expected_cos = round(float(np.cos(2 * np.pi * expected_doy / 365.25)), 6)

        cal = entry["calendar_features"]
        assert cal["target_doy"] == expected_doy
        assert abs(cal[f"doy_sin_h{h}"] - expected_sin) < 1e-4
        assert abs(cal[f"doy_cos_h{h}"] - expected_cos) < 1e-4


def test_6_d1_and_d2_features_differ():
    """TEST 6: D+1 and D+2 are not accidentally using identical feature vectors when date-derived features should differ."""
    diag = get_horizon_diagnostics(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)
    h1_diag = next(d for d in diag["diagnostics"] if d["horizon"] == 1)
    h2_diag = next(d for d in diag["diagnostics"] if d["horizon"] == 2)

    # Feature signatures (hashes) must differ
    assert h1_diag["feature_signature"] != h2_diag["feature_signature"]

    # Target dates must differ
    assert h1_diag["target_date"] != h2_diag["target_date"]

    # Calendar features must differ
    assert h1_diag["calendar_features"]["target_doy"] != h2_diag["calendar_features"]["target_doy"]


# ---------------------------------------------------------------------------
# TEST 7, 8, 9: Timeline Cards & Day Inspector Synchronization
# ---------------------------------------------------------------------------

def test_7_timeline_cards_match_backend_authoritative():
    """TEST 7: Timeline card values match backend authoritative values."""
    tl = get_operational_timeline(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)
    diag = get_horizon_diagnostics(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)

    for h in range(1, 13):
        tl_item = next(d for d in tl["timeline"] if d["day_offset"] == h)
        diag_item = next(d for d in diag["diagnostics"] if d["horizon"] == h)

        assert tl_item["temp_avg_c"] == diag_item["final_prediction"]["temp_avg"]
        assert tl_item["temp_min_c"] == diag_item["final_prediction"]["temp_min"]
        assert tl_item["temp_max_c"] == diag_item["final_prediction"]["temp_max"]
        assert tl_item["rainfall_mm"] == diag_item["final_prediction"]["rainfall_amt"]
        assert tl_item["rain_probability"] == diag_item["final_prediction"]["rain_prob"]
        assert tl_item["wind_kmh"] == diag_item["final_prediction"]["wind_speed"]
        assert tl_item["pressure_hpa"] == diag_item["final_prediction"]["air_pressure"]


def test_8_day_inspector_d7_matches_backend_h7():
    """TEST 8: Day Inspector D+7 matches backend H7."""
    tl = get_operational_timeline(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)
    d7_item = next(d for d in tl["timeline"] if d["day_offset"] == 7)

    diag = get_horizon_diagnostics(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)
    h7_diag = next(d for d in diag["diagnostics"] if d["horizon"] == 7)

    assert d7_item["date"] == h7_diag["target_date"]
    assert d7_item["temp_avg_c"] == h7_diag["final_prediction"]["temp_avg"]
    assert d7_item["temp_min_c"] == h7_diag["final_prediction"]["temp_min"]
    assert d7_item["temp_max_c"] == h7_diag["final_prediction"]["temp_max"]
    assert d7_item["rainfall_mm"] == h7_diag["final_prediction"]["rainfall_amt"]
    assert d7_item["rain_probability"] == h7_diag["final_prediction"]["rain_prob"]
    assert d7_item["wind_kmh"] == h7_diag["final_prediction"]["wind_speed"]
    assert d7_item["pressure_hpa"] == h7_diag["final_prediction"]["air_pressure"]
    assert d7_item["status"] == "FORECAST"


def test_9_day_inspector_d12_matches_backend_h12():
    """TEST 9: Day Inspector D+12 matches backend H12."""
    tl = get_operational_timeline(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)
    d12_item = next(d for d in tl["timeline"] if d["day_offset"] == 12)

    diag = get_horizon_diagnostics(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)
    h12_diag = next(d for d in diag["diagnostics"] if d["horizon"] == 12)

    assert d12_item["date"] == h12_diag["target_date"]
    assert d12_item["temp_avg_c"] == h12_diag["final_prediction"]["temp_avg"]
    assert d12_item["temp_min_c"] == h12_diag["final_prediction"]["temp_min"]
    assert d12_item["temp_max_c"] == h12_diag["final_prediction"]["temp_max"]
    assert d12_item["rainfall_mm"] == h12_diag["final_prediction"]["rainfall_amt"]
    assert d12_item["rain_probability"] == h12_diag["final_prediction"]["rain_prob"]
    assert d12_item["wind_kmh"] == h12_diag["final_prediction"]["wind_speed"]
    assert d12_item["pressure_hpa"] == h12_diag["final_prediction"]["air_pressure"]
    assert d12_item["status"] == "FORECAST"


# ---------------------------------------------------------------------------
# TEST 10, 11, 12: Physical Consistency & Valid Numerical Ranges
# ---------------------------------------------------------------------------

def test_10_tmin_le_tavg_le_tmax():
    """TEST 10: Tmin ≤ Tavg ≤ Tmax for all horizons."""
    tl = get_operational_timeline(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)
    for d in tl["timeline"]:
        if d["day_offset"] > 0:
            tmin = d["temp_min_c"]
            tavg = d["temp_avg_c"]
            tmax = d["temp_max_c"]
            assert tmin <= tavg, f"Ordering violation at day {d['day_offset']}: tmin={tmin} > tavg={tavg}"
            assert tavg <= tmax, f"Ordering violation at day {d['day_offset']}: tavg={tavg} > tmax={tmax}"


def test_11_rainfall_non_negative():
    """TEST 11: Rainfall ≥ 0 for all horizons."""
    tl = get_operational_timeline(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)
    for d in tl["timeline"]:
        if d["day_offset"] > 0 and d["rainfall_mm"] is not None:
            assert d["rainfall_mm"] >= 0.0, f"Negative rainfall at day {d['day_offset']}: {d['rainfall_mm']}"


def test_12_pop_between_0_and_100():
    """TEST 12: PoP ∈ [0, 100]% (in 0.0 to 1.0 probability range)."""
    tl = get_operational_timeline(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)
    for d in tl["timeline"]:
        if d["day_offset"] > 0 and d["rain_probability"] is not None:
            pop = d["rain_probability"]
            assert 0.0 <= pop <= 1.0, f"Invalid probability at day {d['day_offset']}: {pop}"


# ---------------------------------------------------------------------------
# TEST 13, 14, 15: No Artificial Noise, Placeholders, or Recursive Smoothing
# ---------------------------------------------------------------------------

def test_13_no_random_perturbation_deterministic():
    """TEST 13: No random/noise/visual perturbation is applied (deterministic repeatability)."""
    res1 = get_operational_timeline(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)
    res2 = get_operational_timeline(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)

    # Consecutive runs must return bitwise identical predictions
    for d1, d2 in zip(res1["timeline"], res2["timeline"]):
        assert d1["temp_avg_c"] == d2["temp_avg_c"]
        assert d1["temp_min_c"] == d2["temp_min_c"]
        assert d1["temp_max_c"] == d2["temp_max_c"]
        assert d1["rain_probability"] == d2["rain_probability"]
        assert d1["rainfall_mm"] == d2["rainfall_mm"]


def test_14_no_placeholder_probability_formula():
    """TEST 14: No placeholder probability formula remains in the forecast pathway."""
    diag = get_horizon_diagnostics(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)
    # Check that probability varies according to classifier outputs rather than a constant placeholder
    probs = [d["final_prediction"]["rain_prob"] for d in diag["diagnostics"]]
    assert len(set(probs)) > 1, f"Probabilities appear static/constant across horizons: {probs}"


def test_15_no_recursive_smoothing():
    """TEST 15: No recursive smoothing replaces direct horizon model predictions."""
    diag = get_horizon_diagnostics(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)
    # Verify that final_prediction temp_avg matches raw_prediction temp_avg (rounded to 1 decimal)
    for d in diag["diagnostics"]:
        raw_rounded = round(d["raw_prediction"]["temp_avg"], 1)
        final_val = d["final_prediction"]["temp_avg"]
        assert abs(raw_rounded - final_val) < 1e-4, f"Horizon {d['horizon']} prediction modified by smoothing: raw {raw_rounded} vs final {final_val}"


# ---------------------------------------------------------------------------
# TEST 16, 17, 18, 19, 20: Operational, Replay, Provenance & Benchmark Isolation
# ---------------------------------------------------------------------------

def test_16_replay_mode_pinned_to_2025_01_20():
    """TEST 16: Replay mode remains pinned to 2025-01-20."""
    tl = get_operational_timeline(TEST_STATION, mode="historical_holdout_replay")
    assert tl["forecast_origin"] == "2025-01-20"
    d0_item = next(d for d in tl["timeline"] if d["day_offset"] == 0)
    assert d0_item["date"] == "2025-01-20"


def test_17_operational_mode_dynamic_date():
    """TEST 17: Operational mode remains dynamically date-based."""
    dynamic_date = "2026-09-17"
    tl = get_operational_timeline(TEST_STATION, mode="operational_current", origin_date=dynamic_date)
    assert tl["forecast_origin"] == dynamic_date
    d0_item = next(d for d in tl["timeline"] if d["day_offset"] == 0)
    assert d0_item["date"] == dynamic_date


def test_18_d0_observation_only():
    """TEST 18: D0 remains observation-only (never synthesized with model estimates)."""
    # In operational current without live API telemetry, D0 must be UNAVAILABLE, never synthesized
    tl = get_operational_timeline(TEST_STATION, mode="operational_current", origin_date="2026-09-17")
    d0_item = next(d for d in tl["timeline"] if d["day_offset"] == 0)
    assert d0_item["status"] in ("CURRENT", "UNAVAILABLE")
    if d0_item["status"] == "UNAVAILABLE":
        assert d0_item["temp_avg_c"] is None
        assert d0_item["is_observed"] is False


def test_19_forecast_days_remain_forecast():
    """TEST 19: Forecast days remain FORECAST with authoritative engine provenance."""
    tl = get_operational_timeline(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)
    for d in tl["timeline"]:
        if d["day_offset"] > 0:
            assert d["status"] == "FORECAST", f"Day {d['day_offset']} status is {d['status']}, expected FORECAST"
            assert "XGBoost" in d["provenance"] or "FORECAST" in d["provenance"]


def test_20_no_external_forecast_in_prediction():
    """TEST 20: No external forecast is used as our prediction source."""
    diag = get_horizon_diagnostics(TEST_STATION, mode="historical_holdout_replay", origin_date=REPLAY_ORIGIN)
    for d in diag["diagnostics"]:
        assert "Open-Meteo" not in d["provenance"]
        assert "Google" not in d["provenance"]
        assert "AccuWeather" not in d["provenance"]
        assert "XGBoost Multi-Horizon Direct Engine" in d["provenance"]
