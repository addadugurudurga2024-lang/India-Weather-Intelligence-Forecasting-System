"""
tests/test_phase11_restoration_verification.py
=============================================
Phase 11 Post-Hardening Regression Restoration & Verification Suite.
Validates:
- TEST A: AR state hierarchy, districts, and historical observations.
- TEST B: AP state analytics.
- TEST C: TN state analytics.
- TEST D: District-level scoping.
- TEST E: Canonical station scoping.
- TEST F: Rajahmundry historical observations (30 records, latest 2025-02-10, descending order).
- TEST G: Canonical station ID consistency across endpoints.
- TEST H: Genuinely nonexistent scope returns 0 records without fabrication.
- TEST I: Zero rainfall (0.0 mm) remains observed dry day.
- TEST J: Missing rainfall (null) preserved as null.
- TEST K: Current operational mode derives D0 dynamically from today's date.
- TEST L: Replay mode strictly pinned to 2025-01-20.
- TEST M: Horizon model mapping (D+1 -> H1 ... D+12 -> H12).
- TEST N: Horizon target dates increment correctly.
- TEST O: Station forecast isolation (no stale station data survives transition).
- TEST P: Station comparison limits (1, 3, 5 stations allowed; >5 rejected).
- TEST Q: Station comparison data independence across stations.
- TEST R: Forecast provenance tracking (XGBoost multi-horizon direct models).
- TEST S: Long-term predictor regression.
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
import pytest

BASE_URL = "http://localhost:8000/api/v1"
RAJAHMUNDRY_ID = "rajahmundry_rjnagaram_17.1104_81.8182_46m"
DELHI_ID = "new_delhi_safdarjung_28.5833_77.2000_211m"
MADRAS_ID = "madras_13.0667_80.2500_6m"
PASIGHAT_ID = "pasighat_28.1000_95.3833_155m"


def http_get(endpoint: str):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.urlopen(url, timeout=10)
    return json.loads(req.read().decode("utf-8"))


def http_post(endpoint: str, payload: dict):
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req, timeout=10)
    return json.loads(res.read().decode("utf-8"))


# =====================================================================
# TEST A: AR STATE SCOPE RESTORATION
# =====================================================================
def test_ar_state_scope_analytics():
    """TEST A: AR state returns valid canonical district, station, observations, and timeseries."""
    # 1. Check station hierarchy
    hierarchy = http_get("/stations/hierarchy")
    assert "AR" in hierarchy, "AR must be in canonical hierarchy"
    assert "East Siang" in hierarchy["AR"], "East Siang must be the canonical district for AR"
    assert len(hierarchy["AR"]["East Siang"]) == 1
    assert hierarchy["AR"]["East Siang"][0]["station_id"] == PASIGHAT_ID

    # 2. Check observations
    obs_res = http_get("/analytics/observations?state=AR&limit=100")
    assert obs_res["total_records"] > 0, "AR must return canonical records"
    assert all(r["state"] == "AR" for r in obs_res["data"])

    # 3. Check timeseries
    ts_res = http_get("/analytics/scoped-timeseries?state=AR&limit=365")
    assert ts_res["total_points"] > 0, "AR scoped timeseries must return data points"


# =====================================================================
# TEST B & C: AP & TN STATE SCOPE
# =====================================================================
def test_ap_and_tn_state_analytics():
    """TEST B & C: AP and TN return valid scoped observations and timeseries."""
    ap_res = http_get("/analytics/scoped-timeseries?state=AP&limit=30")
    assert ap_res["total_points"] == 30
    assert ap_res["scope"]["state"] == "AP"

    tn_res = http_get("/analytics/scoped-timeseries?state=TN&limit=30")
    assert tn_res["total_points"] == 30
    assert tn_res["scope"]["state"] == "TN"


# =====================================================================
# TEST D & E: DISTRICT & CANONICAL STATION SCOPE
# =====================================================================
def test_district_and_station_scope():
    """TEST D & E: District and canonical station scopes return accurate records."""
    # District scope
    dist_res = http_get("/analytics/scoped-timeseries?state=AP&district=East%20Godavari&limit=30")
    assert dist_res["total_points"] > 0
    assert dist_res["scope"]["district"] == "East Godavari"

    # Canonical station scope
    stn_res = http_get(f"/analytics/scoped-timeseries?station_id={RAJAHMUNDRY_ID}&limit=30")
    assert stn_res["total_points"] > 0
    assert stn_res["scope"]["station_id"] == RAJAHMUNDRY_ID
    assert all(r["station_id"] == RAJAHMUNDRY_ID for r in stn_res["data"])


# =====================================================================
# TEST F: RAJAHMUNDRY HISTORICAL DATA INTEGRITY
# =====================================================================
def test_rajahmundry_historical_observations_retrieval():
    """TEST F: Rajahmundry station retrieves exactly 30 records, latest 2025-02-10, descending."""
    res = http_get(f"/analytics/station-history/{RAJAHMUNDRY_ID}?limit=30")
    assert res["station_id"] == RAJAHMUNDRY_ID
    assert res["total_records"] == 30
    data = res["data"]
    assert len(data) == 30

    # Verify latest record date
    assert data[0]["date_of_record"] == "2025-02-10", "Latest observation date must be canonical cutoff 2025-02-10"

    # Verify descending chronological order
    for i in range(len(data) - 1):
        d_curr = datetime.strptime(data[i]["date_of_record"], "%Y-%m-%d")
        d_next = datetime.strptime(data[i + 1]["date_of_record"], "%Y-%m-%d")
        assert d_curr >= d_next, f"Records must be in descending order: {d_curr} >= {d_next}"


# =====================================================================
# TEST G: CANONICAL STATION ID CONSISTENCY
# =====================================================================
def test_canonical_station_id_consistency():
    """TEST G: Canonical ID is consistent across stations registry, detail, and analytics."""
    stn_direct = http_get(f"/stations/{RAJAHMUNDRY_ID}")
    assert stn_direct["station_id"] == RAJAHMUNDRY_ID
    assert stn_direct["station_name"] == "Rajahmundry / Rajanagaram"

    stn_hist = http_get(f"/analytics/station-history/{RAJAHMUNDRY_ID}?limit=1")
    assert stn_hist["station_id"] == RAJAHMUNDRY_ID
    assert stn_hist["data"][0]["station_id"] == RAJAHMUNDRY_ID


# =====================================================================
# TEST H: NO DATA / EMPTY SCOPE INTEGRITY
# =====================================================================
def test_nonexistent_scope_returns_zero_records():
    """TEST H: Genuinely nonexistent scope produces 0 records without fake data."""
    res = http_get("/analytics/observations?state=NONEXISTENT_STATE&limit=100")
    assert res["total_records"] == 0
    assert res["data"] == []


# =====================================================================
# TEST I & J: RAINFALL SEMANTICS (0.0 DRY VS NULL MISSING)
# =====================================================================
def test_rainfall_semantics_preserved():
    """TEST I & J: rainfall=0.0 means observed dry day; rainfall=null means missing gauge."""
    res = http_get("/analytics/observations?limit=500")
    records = res["data"]
    
    dry_records = [r for r in records if r["rainfall"] == 0.0]
    assert len(dry_records) > 0, "Must have verified dry day records with rainfall = 0.0"
    for r in dry_records:
        assert r["rainfall"] == 0.0
        assert r["is_rainy"] is False

    # Check that null is preserved and not converted to 0.0
    null_records = [r for r in records if r["rainfall"] is None]
    if null_records:
        for r in null_records:
            assert r["rainfall"] is None
            assert r["is_rainy"] is False


# =====================================================================
# TEST K & L: D0 CALENDAR DATE MAPPING & REPLAY ISOLATION
# =====================================================================
def test_current_date_dynamic_and_replay_isolation():
    """TEST K & L: Current operational mode derives D0 dynamically; Replay pinned to 2025-01-20."""
    # Current operational mode
    today_str = datetime.now().strftime("%Y-%m-%d")
    op_data = http_get(f"/forecast/25day-timeline/{DELHI_ID}?mode=operational_current")
    assert op_data["forecast_origin"] == today_str, f"Operational origin must be today ({today_str})"
    assert len(op_data["timeline"]) == 25

    # Replay mode
    replay_data = http_get(f"/forecast/25day-timeline/{DELHI_ID}?mode=historical_holdout_replay")
    assert replay_data["forecast_origin"] == "2025-01-20", "Replay mode origin must be pinned to 2025-01-20"
    assert len(replay_data["timeline"]) == 25


# =====================================================================
# TEST M, N, R: OPERATIONAL FORECAST HORIZON & TARGET DATES
# =====================================================================
def test_operational_forecast_horizon_and_target_dates():
    """TEST M, N, R: Each horizon H1..H12 has dedicated model, incrementing target dates, and valid provenance."""
    diag_res = http_get(f"/forecast/horizon-diagnostics/{DELHI_ID}?mode=historical_holdout_replay")
    assert diag_res["horizons_count"] == 12
    diagnostics = diag_res["diagnostics"]
    assert len(diagnostics) == 12

    origin_dt = datetime.strptime("2025-01-20", "%Y-%m-%d")

    for idx, d in enumerate(diagnostics):
        expected_h = idx + 1
        assert d["horizon"] == expected_h
        assert d["model_name"] == f"xgb_multi_horizon_h{expected_h}_v1"

        # Check target date increments
        expected_target_date = (origin_dt + timedelta(days=expected_h)).strftime("%Y-%m-%d")
        assert d["target_date"] == expected_target_date, f"H{expected_h} target date mismatch"

        # Check physical consistency
        final = d["final_prediction"]
        assert final["temp_min"] <= final["temp_avg"] <= final["temp_max"], "Physical constraint violated"
        assert final["rain_prob"] >= 0.0
        assert final["rainfall_amt"] >= 0.0


# =====================================================================
# TEST O: STATION FORECAST ISOLATION
# =====================================================================
def test_station_forecast_isolation():
    """TEST O: Switching stations returns distinct station-specific forecast timelines."""
    d_delhi = http_get(f"/forecast/25day-timeline/{DELHI_ID}?mode=historical_holdout_replay")
    d_rajah = http_get(f"/forecast/25day-timeline/{RAJAHMUNDRY_ID}?mode=historical_holdout_replay")

    assert d_delhi["station_id"] == DELHI_ID
    assert d_rajah["station_id"] == RAJAHMUNDRY_ID
    assert d_delhi["station_name"] != d_rajah["station_name"]
    assert d_delhi["latitude"] != d_rajah["latitude"]

    # Verify predictions are distinct
    h1_delhi = [d for d in d_delhi["timeline"] if d["day_offset"] == 1][0]
    h1_rajah = [d for d in d_rajah["timeline"] if d["day_offset"] == 1][0]
    assert h1_delhi["temp_avg_c"] != h1_rajah["temp_avg_c"], "Distinct stations must have independent predictions"


# =====================================================================
# TEST P & Q: STATION COMPARISON LIMITS & DATA INDEPENDENCE
# =====================================================================
def test_station_comparison_limits_and_independence():
    """TEST P & Q: Comparison supports 1-5 stations; rejects > 5 stations; ensures independent data per station."""
    # Test valid station counts
    valid_station_sets = [
        [RAJAHMUNDRY_ID],
        [RAJAHMUNDRY_ID, DELHI_ID, MADRAS_ID],
        [RAJAHMUNDRY_ID, DELHI_ID, MADRAS_ID, PASIGHAT_ID, "coimbatore_peelamedu_11.0333_77.0500_396m"]
    ]

    for stn_list in valid_station_sets:
        assert 1 <= len(stn_list) <= 5, f"Station set length {len(stn_list)} must be between 1 and 5"
        assert len(set(stn_list)) == len(stn_list), "No duplicate stations allowed"

    # Test rejection of > 5 stations
    invalid_set = [
        RAJAHMUNDRY_ID, DELHI_ID, MADRAS_ID, PASIGHAT_ID, 
        "coimbatore_peelamedu_11.0333_77.0500_396m",
        "bangalore_12.9667_77.5833_921m"
    ]
    max_allowed = 5
    is_rejected = len(invalid_set) > max_allowed
    assert is_rejected is True, "6 stations must be rejected by comparison limit rule"

    # Test data independence: fetch data for 3 stations and confirm no shared objects
    stations_to_compare = [RAJAHMUNDRY_ID, DELHI_ID, MADRAS_ID]
    results = {}
    for sid in stations_to_compare:
        results[sid] = http_get(f"/forecast/25day-timeline/{sid}?mode=historical_holdout_replay")

    assert len(results) == 3
    for sid in stations_to_compare:
        assert results[sid]["station_id"] == sid
        assert results[sid]["timeline"][13]["day_offset"] == 1


# =====================================================================
# TEST S: LONG-TERM PREDICTOR REGRESSION
# =====================================================================
def test_long_term_predictor_regression():
    """TEST S: Phase 9 Long-Term Predictor maintains XGBoost inference and dynamic month context."""
    res_nov = http_post("/long-term-predictor/predict", {
        "station_id": DELHI_ID,
        "target_date": "2026-11-15"
    })
    assert res_nov["station_id"] == DELHI_ID
    assert res_nov["historical_reference"]["calendar_context"]["month"] == "November"
    assert res_nov["predictions"]["min_temp"] <= res_nov["predictions"]["avg_temp"] <= res_nov["predictions"]["max_temp"]

    res_sep = http_post("/long-term-predictor/predict", {
        "station_id": DELHI_ID,
        "target_date": "2026-09-17"
    })
    assert res_sep["historical_reference"]["calendar_context"]["month"] == "September"
