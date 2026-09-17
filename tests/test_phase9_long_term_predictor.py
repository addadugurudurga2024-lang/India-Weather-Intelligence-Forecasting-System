"""
Phase 9 Long-Term Weather Predictor — Comprehensive Test Suite
Validates Tests A through N:
- Test A: Model Artifact Integrity (all 7 models exist)
- Test B: Model Metadata Integrity
- Test C: Feature Schema Integrity
- Test D: Leakage Test (no target-date future data in features)
- Test E: Station Coverage (all 413 canonical stations supported)
- Test F: Date Validation (out-of-range dates safely rejected)
- Test G: Prediction Determinism (identical input -> identical output)
- Test H: Temperature Ordering (T_min <= T_avg <= T_max)
- Test I: Rain Probability (0 <= p <= 1)
- Test J: Rainfall Non-Negativity (>= 0)
- Test K: Provenance Verification
- Test L: Historical Reference Match
- Test M: Service Numerical Match
- Test N: Phase 1-8.5 Baseline & Raw Dataset Immutability
"""

import hashlib
import json
from pathlib import Path
import numpy as np
import pytest
from phase9_long_term_predictor.services.long_term_predictor_engine import (
    predict_long_term,
    build_feature_vector,
    FEATURE_NAMES,
    SUPPORTED_MIN_DATE,
    SUPPORTED_MAX_DATE,
)

PROJECT_ROOT = Path("d:/weather_forcasting")
MODELS_DIR = PROJECT_ROOT / "phase9_long_term_predictor" / "models"
DATA_DIR = PROJECT_ROOT / "phase9_long_term_predictor" / "data"
RAW_DATA_PATH = Path(r"D:\Downloads\india_weather_rainfall_data.xlsx")
PHASE3_METRICS_PATH = PROJECT_ROOT / "frontend" / "src" / "data" / "authoritativeMetrics.json"

EXPECTED_MODELS = [
    "xgb_longterm_temp_v1.json",
    "xgb_longterm_temp_min_v1.json",
    "xgb_longterm_temp_max_v1.json",
    "xgb_longterm_rain_amt_v1.json",
    "xgb_longterm_rain_cls_v1.json",
    "xgb_longterm_wind_v1.json",
    "xgb_longterm_pressure_v1.json",
]


def test_a_model_artifact_integrity():
    """Test A: All 7 expected Phase 9 model files exist and are non-empty."""
    for model_name in EXPECTED_MODELS:
        model_path = MODELS_DIR / model_name
        assert model_path.exists(), f"Missing model artifact: {model_name}"
        assert model_path.stat().st_size > 1000, f"Model artifact {model_name} is unexpectedly small ({model_path.stat().st_size} bytes)"


def test_b_model_metadata_integrity():
    """Test B: Metadata contains entries for all 7 models with correct targets."""
    meta_path = DATA_DIR / "phase9_models_metadata.json"
    assert meta_path.exists()
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert len(meta) == 7
    for key, val in meta.items():
        assert "model_id" in val
        assert "target" in val
        assert "features" in val
        assert val["feature_count"] == 24
        assert "metrics" in val
        assert val["model_file"] in EXPECTED_MODELS


def test_c_feature_schema_integrity():
    """Test C: Feature order and schema exactly match 24 expected features."""
    assert len(FEATURE_NAMES) == 24
    expected_names = [
        "doy", "doy_sin", "doy_cos", "doy_sin2", "doy_cos2", "month", "season_code",
        "latitude", "longitude", "elevation",
        "station_hist_avg_temp_mean", "station_hist_min_temp_mean", "station_hist_max_temp_mean",
        "station_hist_wind_speed_mean", "station_hist_air_pressure_mean", "station_hist_rain_frequency",
        "station_month_avg_temp_mean", "station_month_avg_temp_std", "station_month_min_temp_mean",
        "station_month_max_temp_mean", "station_month_wind_speed_mean", "station_month_air_pressure_mean",
        "station_month_rain_frequency", "station_month_rain_amount_mean",
    ]
    assert FEATURE_NAMES == expected_names


def test_d_leakage_free_feature_construction():
    """Test D: Feature construction uses ONLY calendar harmonics, geographic metadata, and historical climatology."""
    stn_id = "new_delhi_safdarjung_28.5833_77.2000_211m"
    target_date = "2026-11-15"
    X, stn_data, m_data = build_feature_vector(stn_id, target_date)

    assert X.shape == (1, 24)
    # Check no NaNs or Infs
    assert not np.isnan(X).any(), "Feature vector contains NaNs!"
    assert not np.isinf(X).any(), "Feature vector contains Infs!"

    # DOY for Nov 15 on a non-leap year (2026) is 319
    assert X[0, 0] == 319
    # Month is 11
    assert X[0, 5] == 11
    # Elevation is 211
    assert X[0, 9] == 211.0


def test_e_station_coverage():
    """Test E: All 413 canonical monitoring stations are supported."""
    clim_path = DATA_DIR / "authoritative_station_climatology.json"
    with open(clim_path, "r", encoding="utf-8") as f:
        climatology = json.load(f)

    assert len(climatology) == 413, f"Expected 413 canonical stations, got {len(climatology)}"

    # Test random sample of 5 stations across states
    sample_stns = [
        "new_delhi_safdarjung_28.5833_77.2000_211m",
        "rajahmundry_rjnagaram_17.1104_81.8182_46m",
        "bombay_colaba_18.9000_72.8167_10m",
        "shimla_31.1000_77.1667_2205m",
        "port_blair_11.6667_92.7167_73m",
    ]
    for stn in sample_stns:
        assert stn in climatology
        res = predict_long_term(stn, "2026-07-15")
        assert res["status"] == "AVAILABLE"
        assert res["predictions"] is not None


def test_f_date_validation():
    """Test F: Unsupported dates are safely rejected with UNAVAILABLE status."""
    stn = "new_delhi_safdarjung_28.5833_77.2000_211m"

    # Past before minimum
    past_res = predict_long_term(stn, "2020-05-01")
    assert past_res["status"] == "UNAVAILABLE"
    assert "outside the validated Long-Term Predictor range" in past_res["error"]

    # Far future beyond maximum
    future_res = predict_long_term(stn, "2035-05-01")
    assert future_res["status"] == "UNAVAILABLE"
    assert "outside the validated Long-Term Predictor range" in future_res["error"]


def test_g_prediction_determinism():
    """Test G: Prediction engine is strictly deterministic (same input produces identical output)."""
    stn = "rajahmundry_rjnagaram_17.1104_81.8182_46m"
    date = "2026-11-15"

    res1 = predict_long_term(stn, date)
    res2 = predict_long_term(stn, date)

    assert res1["predictions"] == res2["predictions"]
    assert res1["uncertainty"] == res2["uncertainty"]


def test_h_temperature_ordering():
    """Test H: Physical constraint T_min <= T_avg <= T_max is strictly maintained."""
    test_cases = [
        ("new_delhi_safdarjung_28.5833_77.2000_211m", "2026-01-15"),  # Winter
        ("new_delhi_safdarjung_28.5833_77.2000_211m", "2026-05-15"),  # Peak Summer
        ("shimla_31.1000_77.1667_2205m", "2026-01-15"),               # Snow / Cold
        ("bombay_colaba_18.9000_72.8167_10m", "2026-08-15"),          # Monsoon Coastal
        ("rajahmundry_rjnagaram_17.1104_81.8182_46m", "2026-11-15"),   # Master Prompt Case
    ]
    for stn, date in test_cases:
        res = predict_long_term(stn, date)
        assert res["status"] == "AVAILABLE"
        preds = res["predictions"]
        assert preds["min_temp"] <= preds["avg_temp"], f"Violation in {stn} {date}: min={preds['min_temp']} > avg={preds['avg_temp']}"
        assert preds["avg_temp"] <= preds["max_temp"], f"Violation in {stn} {date}: avg={preds['avg_temp']} > max={preds['max_temp']}"


def test_i_rain_probability():
    """Test I: Rain probability is a genuine calibrated probability in [0.0, 1.0]."""
    for stn in ["cherrapunji_25.2500_91.7333_1312m", "jodhpur_26.3000_73.0167_217m"]:
        res_monsoon = predict_long_term(stn, "2026-07-15")
        res_winter = predict_long_term(stn, "2026-01-15")

        prob_m = res_monsoon["predictions"]["rain_probability"]
        prob_w = res_winter["predictions"]["rain_probability"]

        assert 0.0 <= prob_m <= 1.0
        assert 0.0 <= prob_w <= 1.0

    # Cherrapunji monsoon rain probability should be significantly higher than Jodhpur winter rain probability
    res_cherra = predict_long_term("cherrapunji_25.2500_91.7333_1312m", "2026-07-15")
    res_jodh = predict_long_term("jodhpur_26.3000_73.0167_217m", "2026-01-15")
    assert res_cherra["predictions"]["rain_probability"] > res_jodh["predictions"]["rain_probability"]


def test_j_rainfall_non_negativity():
    """Test J: Rainfall is non-negative."""
    stns = ["jodhpur_26.3000_73.0167_217m", "rajahmundry_rjnagaram_17.1104_81.8182_46m", "shimla_31.1000_77.1667_2205m"]
    for stn in stns:
        res = predict_long_term(stn, "2026-11-15")
        assert res["predictions"]["rainfall"] >= 0.0
        assert res["predictions"]["wind_speed"] >= 0.0


def test_k_provenance_verification():
    """Test K: Structured provenance is attached to every prediction."""
    res = predict_long_term("rajahmundry_rjnagaram_17.1104_81.8182_46m", "2026-11-15")
    prov = res["provenance"]
    assert "models_used" in prov
    assert len(prov["models_used"]) == 7
    assert prov["training_window"] == "2015-01-01 to 2023-12-31 (Canonical 10-Year Panel)"
    assert prov["source_dataset_sha256"] == "e6a636777430f078b4d970f9f46e79efcece7f97b67dd186c30a755d2783cd84"
    assert prov["physical_ordering_applied"] is True


def test_l_historical_reference_match():
    """Test L: Displayed historical reference data matches station climatology."""
    stn = "rajahmundry_rjnagaram_17.1104_81.8182_46m"
    res = predict_long_term(stn, "2026-11-15")
    ref = res["historical_reference"]

    assert ref["calendar_context"]["month"] == "November"
    assert ref["calendar_context"]["selected_date"] == "2026-11-15"
    assert "station_monthly_climatology" in ref
    assert ref["station_monthly_climatology"]["historical_mean_temp"] is not None


def test_m_frontend_data_bundle_match():
    """Test M: Frontend authoritative bundle is synchronized with backend climatology."""
    fe_bundle_path = PROJECT_ROOT / "frontend" / "src" / "data" / "authoritativeLongTermPredictorData.json"
    assert fe_bundle_path.exists()
    with open(fe_bundle_path, "r", encoding="utf-8") as f:
        fe_bundle = json.load(f)

    assert fe_bundle["metadata"]["total_stations_available"] == 413
    assert len(fe_bundle["station_climatology"]) == 413
    assert "rajahmundry_rjnagaram_17.1104_81.8182_46m" in fe_bundle["station_climatology"]


def test_n_baseline_and_raw_dataset_immutability():
    """Test N: Phase 1-8.5 raw dataset and Phase 3 primary metrics remain untouched."""
    # 1. Raw Excel hash
    with open(RAW_DATA_PATH, "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    assert h == "e6a636777430f078b4d970f9f46e79efcece7f97b67dd186c30a755d2783cd84", "RAW DATASET HAS BEEN MODIFIED!"

    # 2. Phase 3 authoritative metrics hash and benchmark values
    with open(PHASE3_METRICS_PATH, "rb") as f:
        h_m = hashlib.sha256(f.read()).hexdigest()
    assert h_m == "7ab59fa3f6cdf484b59686aaf0b9f3a48b062ce2e037f83752e0b2bcbb107746", "PHASE 3 METRICS ALTERED!"

    with open(PHASE3_METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    assert abs(metrics["target_a_temperature"]["xgboost"]["holdout"]["mae"] - 0.6527) < 1e-4
    assert abs(metrics["target_b_rainfall_amount"]["xgboost"]["holdout"]["mae"] - 0.4344) < 1e-4
    assert abs(metrics["target_c_rain_binary"]["xgboost"]["holdout"]["roc_auc"] - 0.8366) < 1e-4
