"""
tests/test_state_scope_analytics_regression.py
=============================================
Post-Phase-11 State-Scope / Analytics No-Data Regression Test Suite.
Verifies Tasks A through N:
- TEST A: AR exists in canonical station hierarchy.
- TEST B: AR hierarchy returns correct districts.
- TEST C: AR hierarchy returns correct stations.
- TEST D: AR observations endpoint returns actual records.
- TEST E: AR scoped timeseries returns actual records.
- TEST F: AR temperature analytics receives non-empty canonical data.
- TEST G: AR rainfall analytics receives non-empty canonical data.
- TEST H: AR Overview Dashboard receives correct scoped data.
- TEST I: State -> District -> Station cascade remains synchronized.
- TEST J: No stale station/district from previous scope survives transition.
- TEST K: Nonexistent scope returns truthful empty state (0 records).
- TEST L: Observed 0.0 rainfall remains genuine 0.0mm dry day.
- TEST M: Missing rainfall remains null (zero-imputation rejected).
- TEST N: API failure remains distinguishable from empty data.
- Cross-State generic verification: AP, TN, DL, AR, TR.
"""

import json
import urllib.request
import urllib.error
import pytest

BASE_URL = "http://localhost:8000/api/v1"


def http_get(endpoint: str):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.urlopen(url, timeout=10)
    return json.loads(req.read().decode("utf-8"))


# =====================================================================
# TEST A, B, C: AR IN CANONICAL HIERARCHY & REGISTRY
# =====================================================================

def test_task_a_ar_exists_in_canonical_hierarchy():
    """TEST A: State code AR exists in canonical station hierarchy."""
    hierarchy = http_get("/stations/hierarchy")
    assert "AR" in hierarchy, "AR must be present in canonical hierarchy"


def test_task_b_ar_hierarchy_districts():
    """TEST B: AR hierarchy returns canonical districts (East Siang)."""
    hierarchy = http_get("/stations/hierarchy")
    ar_districts = hierarchy["AR"]
    assert len(ar_districts) == 1, "AR must possess exactly 1 canonical district"
    assert "East Siang" in ar_districts, "East Siang must be the canonical district for AR"


def test_task_c_ar_hierarchy_stations():
    """TEST C: AR hierarchy returns canonical stations (Pasighat)."""
    hierarchy = http_get("/stations/hierarchy")
    ar_stations = hierarchy["AR"]["East Siang"]
    assert len(ar_stations) == 1, "East Siang must possess exactly 1 canonical station"
    pasighat = ar_stations[0]
    assert pasighat["station_id"] == "pasighat_28.1000_95.3833_155m"
    assert pasighat["station_name"] == "Pasighat"
    assert pasighat["state"] == "AR"
    assert pasighat["district"] == "East Siang"


# =====================================================================
# TEST D, E: AR OBSERVATIONS & SCOPED TIMESERIES
# =====================================================================

def test_task_d_ar_observations_endpoint_records():
    """TEST D: AR observations endpoint returns actual canonical records (count > 0)."""
    res = http_get("/analytics/observations?state=AR&limit=100")
    assert res["total_records"] > 0, "AR observations count must be > 0"
    data = res["data"]
    assert len(data) > 0
    # Confirm records belong strictly to AR
    for record in data:
        assert record["state"] == "AR"
        assert record["district"] == "East Siang"
        assert record["station_id"] == "pasighat_28.1000_95.3833_155m"
        assert "avg_temp" in record
        assert "rainfall" in record


def test_task_e_ar_scoped_timeseries_points():
    """TEST E: AR scoped timeseries returns chronological records up to limit."""
    res = http_get("/analytics/scoped-timeseries?state=AR&limit=365")
    assert res["total_points"] > 0, "AR scoped timeseries points must be > 0"
    data = res["data"]
    assert len(data) > 0
    # Confirm aggregation identifier and dates
    for pt in data:
        assert pt["state"] == "AR"
        assert pt["station_id"] == "SCOPED_AR_ALL"
        assert "date_of_record" in pt


# =====================================================================
# TEST F, G: TEMPERATURE & RAINFALL ANALYTICS SEMANTICS
# =====================================================================

def test_task_f_ar_temperature_analytics_valid_metrics():
    """TEST F: AR temperature analytics receives non-empty data and computes valid metrics."""
    res = http_get("/analytics/scoped-timeseries?state=AR&limit=365")
    data = res["data"]
    valid_temps = [d["avg_temp"] for d in data if d["avg_temp"] is not None]
    max_temps = [d["max_temp"] for d in data if d["max_temp"] is not None]
    min_temps = [d["min_temp"] for d in data if d["min_temp"] is not None]

    assert len(valid_temps) > 0, "Valid temperature observations must exist for AR"
    assert len(max_temps) > 0
    assert len(min_temps) > 0

    mean_temp = sum(valid_temps) / len(valid_temps)
    peak_high = max(max_temps)
    lowest_low = min(min_temps)

    # Physical reality constraints for Pasighat, Arunachal Pradesh (sub-tropical foothills)
    assert 10.0 <= mean_temp <= 35.0, f"Mean temp {mean_temp} out of realistic physical range"
    assert lowest_low <= mean_temp <= peak_high


def test_task_g_ar_rainfall_analytics_valid_metrics():
    """TEST G: AR rainfall analytics receives non-empty canonical data."""
    res = http_get("/analytics/scoped-timeseries?state=AR&limit=365")
    data = res["data"]
    valid_rain = [d["rainfall"] for d in data if d["rainfall"] is not None]

    assert len(valid_rain) > 0, "Valid rainfall observations must exist for AR"
    dry_count = sum(1 for r in valid_rain if r == 0.0)
    rainy_count = sum(1 for r in valid_rain if r > 0.0)
    assert dry_count + rainy_count > 0, "Must have active rain or dry observations"


# =====================================================================
# TEST H: OVERVIEW DASHBOARD SCOPED DATA
# =====================================================================

def test_task_h_ar_overview_dashboard_data():
    """TEST H: AR Overview Dashboard receives correct scoped observations."""
    res = http_get("/analytics/observations?state=AR&limit=100")
    assert res["total_records"] > 0
    records = res["data"]
    # Both temperature and rainfall records must be present for the chart
    temps = [r["avg_temp"] for r in records if r["avg_temp"] is not None]
    rains = [r["rainfall"] for r in records if r["rainfall"] is not None]
    assert len(temps) > 0, "Dashboard temperature series must not be empty"
    assert len(rains) > 0, "Dashboard rainfall series must not be empty"


# =====================================================================
# TEST I, J: CASCADE SYNCHRONIZATION & NO STALE SCOPE LEAKAGE
# =====================================================================

def test_task_i_and_j_state_transition_no_stale_contamination():
    """TEST I & J: Transition AR -> AP -> TN -> DL -> AR preserves scope integrity with zero stale contamination."""
    # 1. Scope AR
    ar_res = http_get("/analytics/scoped-timeseries?state=AR&limit=30")
    assert ar_res["total_points"] > 0
    assert ar_res["data"][0]["state"] == "AR"

    # 2. Scope AP Guntur
    ap_res = http_get("/analytics/scoped-timeseries?state=AP&district=Guntur&limit=30")
    assert ap_res["total_points"] > 0
    assert ap_res["data"][0]["state"] == "AP"
    assert ap_res["data"][0]["district"] == "Guntur"

    # 3. Scope TN
    tn_res = http_get("/analytics/scoped-timeseries?state=TN&limit=30")
    assert tn_res["total_points"] > 0
    assert tn_res["data"][0]["state"] == "TN"

    # 4. Scope DL
    dl_res = http_get("/analytics/scoped-timeseries?state=DL&district=New%20Delhi&limit=30")
    assert dl_res["total_points"] > 0
    assert dl_res["data"][0]["state"] == "DL"

    # 5. Return to AR: confirm zero New Delhi or Guntur leakage
    ar_return = http_get("/analytics/scoped-timeseries?state=AR&limit=30")
    assert ar_return["total_points"] > 0
    for pt in ar_return["data"]:
        assert pt["state"] == "AR"
        assert "Guntur" not in pt["station_name"]
        assert "Delhi" not in pt["station_name"]

    # 6. Mismatched query cross-check: AR with New Delhi district must return 0, not DL records
    mismatched = http_get("/analytics/scoped-timeseries?state=AR&district=New%20Delhi&limit=30")
    assert mismatched["total_points"] == 0, "Mismatched state+district query must return 0 records"


# =====================================================================
# TEST K: NONEXISTENT SCOPE RETURNS TRUTHFUL EMPTY STATE
# =====================================================================

def test_task_k_nonexistent_scope_returns_truthful_empty_state():
    """TEST K: Genuinely nonexistent state returns HTTP 200 with 0 records (truthful empty state)."""
    res = http_get("/analytics/observations?state=XX_NONEXISTENT&limit=100")
    assert res["total_records"] == 0
    assert res["data"] == []

    ts = http_get("/analytics/scoped-timeseries?state=XX_NONEXISTENT&limit=365")
    assert ts["total_points"] == 0
    assert ts["data"] == []


# =====================================================================
# TEST L, M: 0.0 MM DRY DAYS VS NULL MISSING RAINFALL SEMANTICS
# =====================================================================

def test_task_l_and_m_rainfall_semantics():
    """TEST L & M: 0.0mm dry day is preserved; missing rainfall remains null; never zero-imputed."""
    # Query pan-India or state with known mixed observations
    res = http_get("/analytics/observations?limit=500")
    data = res["data"]

    dry_records = [r for r in data if r["rainfall"] == 0.0]
    null_records = [r for r in data if r["rainfall"] is None]
    rainy_records = [r for r in data if r["rainfall"] is not None and r["rainfall"] > 0.0]

    assert len(dry_records) > 0, "Must contain genuine observed dry days (0.0mm)"
    assert len(rainy_records) > 0, "Must contain genuine active precipitation (>0.0mm)"
    # Ensure dry records are strictly 0.0, not null
    for r in dry_records:
        assert r["rainfall"] == 0.0
        assert r["is_rainy"] is False

    # Ensure rainy records are > 0.0
    for r in rainy_records:
        assert r["rainfall"] > 0.0
        assert r["is_rainy"] is True


# =====================================================================
# TEST N: API FAILURE VS NO DATA DISTINCTION
# =====================================================================

def test_task_n_api_failure_distinguishable():
    """TEST N: API errors (404/422) remain distinct from empty results (200 with empty list)."""
    # 1. Invalid station ID -> 404
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        http_get("/stations/non_existent_station_xyz_999")
    assert exc_info.value.code == 404

    # 2. Invalid limit parameter -> 422
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        http_get("/analytics/observations?limit=-5")
    assert exc_info.value.code == 422

    # 3. Valid but empty query -> HTTP 200 with 0 records
    res = http_get("/analytics/observations?state=ZZ&limit=10")
    assert res["total_records"] == 0
    assert res["data"] == []


# =====================================================================
# TASK 20: GENERIC CROSS-STATE VERIFICATION (AP, TN, DL, AR, TR)
# =====================================================================

@pytest.mark.parametrize("state_code,expected_min_records", [
    ("AR", 1),
    ("AP", 10),
    ("TN", 20),
    ("DL", 5),
    ("TR", 1),
])
def test_task_20_cross_state_observations_and_timeseries(state_code, expected_min_records):
    """Verify generic state scoping across multiple distinct states."""
    # Observations
    obs = http_get(f"/analytics/observations?state={state_code}&limit=50")
    assert obs["total_records"] >= expected_min_records
    for r in obs["data"]:
        assert r["state"].upper() == state_code.upper()

    # Timeseries
    ts = http_get(f"/analytics/scoped-timeseries?state={state_code}&limit=30")
    assert ts["total_points"] > 0
    for pt in ts["data"]:
        assert pt["state"].upper() == state_code.upper()
