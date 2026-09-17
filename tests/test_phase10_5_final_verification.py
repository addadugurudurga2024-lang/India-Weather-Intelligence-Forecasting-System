"""Comprehensive automated simulation and contract verification of Tasks 1-13 for Phase 10.5."""

import json
import urllib.request
import pytest
from backend.app.services.data_service import get_scoped_timeseries, get_scoped_observations, get_station_by_id
from phase9_long_term_predictor.services.long_term_predictor_engine import predict_long_term

BASE_URL = "http://localhost:8000/api/v1"


def http_get(endpoint: str):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.urlopen(url, timeout=5)
    return json.loads(req.read().decode("utf-8"))


def http_post(endpoint: str, payload: dict):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req, timeout=5)
    return json.loads(res.read().decode("utf-8"))


def test_task1_and_4_temperature_analytics_scoped_and_transitions():
    """Verify Temperature Analytics across AP Guntur, TN, and Rajahmundry scopes."""
    # 1. AP Guntur (Rentachintala)
    guntur_ts = http_get("/analytics/scoped-timeseries?state=AP&district=Guntur&limit=365")
    assert guntur_ts["total_points"] > 0
    points = guntur_ts["data"]
    valid_temps = [p["avg_temp"] for p in points if p["avg_temp"] is not None]
    assert len(valid_temps) > 0
    mean_temp = sum(valid_temps) / len(valid_temps)
    assert 20.0 < mean_temp < 35.0
    # Confirm latest point is from canonical records
    assert points[-1]["date_of_record"] == "2025-02-10"

    # 2. TN (30 stations aggregation)
    tn_ts = http_get("/analytics/scoped-timeseries?state=TN&limit=365")
    assert tn_ts["total_points"] > 0
    tn_points = tn_ts["data"]
    # Check that TN points are distinct from AP Guntur points
    assert tn_points[-1]["station_id"] == "SCOPED_TN_ALL"
    assert tn_points[-1]["date_of_record"] == "2025-02-10"
    assert tn_points[-1]["avg_temp"] != points[-1]["avg_temp"]

    # 3. Rajahmundry / Rajanagaram
    raj_ts = http_get("/analytics/scoped-timeseries?station_id=rajahmundry_rjnagaram_17.1104_81.8182_46m&limit=365")
    assert raj_ts["total_points"] > 0
    raj_points = raj_ts["data"]
    assert raj_points[-1]["station_id"] == "rajahmundry_rjnagaram_17.1104_81.8182_46m"
    assert raj_points[-1]["date_of_record"] == "2025-02-10"
    assert raj_points[-1]["avg_temp"] == 26.6


def test_task2_rainfall_intelligence_scoped_and_semantics():
    """Verify Rainfall Intelligence metrics and zero/null semantics."""
    # TN Rainfall sequence
    tn_obs = http_get("/analytics/observations?state=TN&limit=100")
    assert tn_obs["total_records"] > 0
    records = tn_obs["data"]
    
    # Check null vs zero
    dry_count = sum(1 for r in records if r["rainfall"] == 0.0)
    missing_count = sum(1 for r in records if r["rainfall"] is None)
    rainy_count = sum(1 for r in records if r["rainfall"] is not None and r["rainfall"] > 0)

    assert dry_count > 0, "Must contain genuine dry observations (0.0mm)"
    # At least dry or rainy days exist
    assert dry_count + rainy_count > 0

    # AP Guntur
    guntur_obs = http_get("/analytics/observations?state=AP&district=Guntur&limit=100")
    assert guntur_obs["total_records"] > 0
    for r in guntur_obs["data"]:
        assert r["district"] == "Guntur"


def test_task3_station_explorer_recent_observations():
    """Verify Station Explorer returns recent canonical records sorted descending."""
    raj_hist = http_get("/analytics/station-history/rajahmundry_rjnagaram_17.1104_81.8182_46m?limit=15")
    assert raj_hist["total_records"] > 0
    records = raj_hist["data"]
    assert len(records) >= 10

    # Check date ordering: latest date first
    dates = [r["date_of_record"] for r in records]
    assert dates == sorted(dates, reverse=True), "Records must be sorted descending by date"
    assert dates[0] == "2025-02-10"
    
    first = records[0]
    assert first["avg_temp"] == 26.6
    assert first["min_temp"] == 22.0
    assert first["max_temp"] == 32.7
    assert first["rainfall"] == 0.0
    assert first["wind_speed"] == 7.1
    assert first["air_pressure"] == 1013.7


def test_task8_and_10_long_term_predictor_inference_and_provenance():
    """Verify Long-Term Predictor live inference and Rajahmundry test cases."""
    # Test A: 2026-11-15
    res_nov = http_post("/long-term-predictor/predict", {
        "station_id": "rajahmundry_rjnagaram_17.1104_81.8182_46m",
        "target_date": "2026-11-15"
    })
    assert res_nov["status"] == "AVAILABLE"
    p_nov = res_nov["predictions"]
    ref_nov = res_nov["historical_reference"]["station_monthly_climatology"]
    
    assert p_nov["avg_temp"] == 26.8
    assert p_nov["min_temp"] == 22.5
    assert p_nov["max_temp"] == 32.2
    assert p_nov["rain_probability_pct"] == 37.5
    assert ref_nov["historical_rain_frequency_pct"] == 41.7
    assert p_nov["rain_probability_pct"] != ref_nov["historical_rain_frequency_pct"]

    # Test B: 2026-09-15
    res_sep = http_post("/long-term-predictor/predict", {
        "station_id": "rajahmundry_rjnagaram_17.1104_81.8182_46m",
        "target_date": "2026-09-15"
    })
    assert res_sep["status"] == "AVAILABLE"
    p_sep = res_sep["predictions"]
    ref_sep = res_sep["historical_reference"]["station_monthly_climatology"]

    assert p_sep["avg_temp"] == 28.7
    assert p_sep["min_temp"] == 25.2
    assert p_sep["max_temp"] == 33.0
    assert p_sep["rain_probability_pct"] == 89.4
    assert ref_sep["historical_rain_frequency_pct"] == 87.9


def test_task12_no_artificial_noise():
    """Confirm determinism: identical inputs produce identical outputs (no random noise)."""
    r1 = predict_long_term("rajahmundry_rjnagaram_17.1104_81.8182_46m", "2026-11-15")
    r2 = predict_long_term("rajahmundry_rjnagaram_17.1104_81.8182_46m", "2026-11-15")
    assert r1["predictions"] == r2["predictions"]
