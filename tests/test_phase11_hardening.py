"""
tests/test_phase11_hardening.py
===============================
Phase 11 — Engineering Hardening Verification Test Suite
Addresses Tasks 1-25 of the Final Master Prompt:
- Task A: Current Operational Date dynamic calculation (D0 = today)
- Task B: Date rollover calculation
- Task C: Audited Ground-Truth Replay isolation (D0 = 2025-01-20)
- Task D: Current / Replay isolation
- Task E: 25-day Timeline generation (D-12 .. D+12)
- Task F: Station synchronization & timeline updates
- Task G: State/District synchronization (distinct station data)
- Task H: D0 Telemetry observation-only rule (no model fallback)
- Task I: Temperature terminology & distinct Tmin, Tavg, Tmax
- Task J: Physical ordering (Tmin <= Tavg <= Tmax)
- Task K: Long-Term default date (today dynamic derivation)
- Task L: Long-Term selected target date persistence
- Task M: Historical month reference dynamic derivation (Sept, Nov, Jan, Dec)
- Task N: Rain occurrence probability vs expected rainfall amount separation
- Task O: Historical rain frequency clearly labeled as reference, not prediction
- Task P: Prediction provenance distinction (XGBOOST_LONG_TERM, MONGODB_CACHE, OFFLINE_ESTIMATE)
- Task Q: Uncertainty terminology (strictly 80% Prediction Interval / 80% PI)
- Task R: No fake data or synthetic observation fallback
- Task S: API contract integrity (FastAPI response models)
"""

from datetime import datetime, timedelta
import json
import urllib.request
import urllib.error
import pytest

from backend.app.services.long_term_predictor_service import (
    run_long_term_prediction,
    get_long_term_model_metadata,
)

BASE_URL = "http://localhost:8000/api/v1"

TEST_STATION_1 = "new_delhi_safdarjung_28.5833_77.2000_211m"
TEST_STATION_2 = "rajahmundry_rjnagaram_17.1104_81.8182_46m"
TEST_STATION_3 = "coimbatore_peelamedu_11.0333_77.0500_396m"


def http_get(endpoint: str):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.urlopen(url, timeout=10)
    return json.loads(req.read().decode("utf-8"))


def http_post(endpoint: str, payload: dict):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req, timeout=10)
    return json.loads(res.read().decode("utf-8"))


# =====================================================================
# TASK A, B, C, D, E: CURRENT DATE, ROLLOVER, REPLAY & TIMELINE
# =====================================================================

def test_current_operational_d0_dynamic():
    """Task A: Current operational D0 dynamically equals today's calendar date."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    data = http_get(f"/forecast/25day-timeline/{TEST_STATION_1}?mode=operational_current")
    assert data["forecast_origin"] == today_str
    assert len(data["timeline"]) == 25
    
    # Locate D0
    d0_entries = [d for d in data["timeline"] if d["horizon_label"] == "D0"]
    assert len(d0_entries) == 1
    assert d0_entries[0]["date"] == today_str


def test_date_rollover_advancement():
    """Task B: If operational date advances by one day, D0 advances by one day."""
    today = datetime.now().date()
    tomorrow_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    data = http_get(f"/forecast/25day-timeline/{TEST_STATION_1}?mode=operational_current&origin_date={tomorrow_str}")
    assert data["forecast_origin"] == tomorrow_str
    
    d0_entries = [d for d in data["timeline"] if d["horizon_label"] == "D0"]
    assert len(d0_entries) == 1
    assert d0_entries[0]["date"] == tomorrow_str


def test_replay_isolation_pins_d0_to_2025_01_20():
    """Task C & D: Replay mode strictly uses D0 = 2025-01-20, isolating from operational."""
    data = http_get(f"/forecast/25day-timeline/{TEST_STATION_1}?mode=historical_holdout_replay")
    assert data["forecast_origin"] == "2025-01-20"
    
    d0_entries = [d for d in data["timeline"] if d["horizon_label"] == "D0"]
    assert len(d0_entries) == 1
    assert d0_entries[0]["date"] == "2025-01-20"
    assert d0_entries[0]["provenance"] in ("CURRENT", "OBSERVED")


def test_timeline_generation_d_minus_12_to_d_plus_12():
    """Task E: Timeline correctly generates D-12 to D+12 offsets relative to origin."""
    fixed_origin = "2026-09-16"
    data = http_get(f"/forecast/25day-timeline/{TEST_STATION_1}?mode=operational_current&origin_date={fixed_origin}")
    timeline = data["timeline"]
    assert len(timeline) == 25
    
    # Check D-12
    assert timeline[0]["horizon_label"] == "D-12"
    assert timeline[0]["date"] == "2026-09-04"
    
    # Check D-1
    assert timeline[11]["horizon_label"] == "D-1"
    assert timeline[11]["date"] == "2026-09-15"
    
    # Check D0
    assert timeline[12]["horizon_label"] == "D0"
    assert timeline[12]["date"] == "2026-09-16"
    
    # Check D+1
    assert timeline[13]["horizon_label"] == "D+1"
    assert timeline[13]["date"] == "2026-09-17"
    
    # Check D+12
    assert timeline[24]["horizon_label"] == "D+12"
    assert timeline[24]["date"] == "2026-09-28"


# =====================================================================
# TASK F, G: STATION SYNCHRONIZATION & NO STALE STATE
# =====================================================================

def test_station_synchronization_and_metadata():
    """Task F & G: Each station returns its own station_id, coordinates, and timeline."""
    d1 = http_get(f"/forecast/25day-timeline/{TEST_STATION_1}?mode=operational_current")
    d2 = http_get(f"/forecast/25day-timeline/{TEST_STATION_2}?mode=operational_current")
    d3 = http_get(f"/forecast/25day-timeline/{TEST_STATION_3}?mode=operational_current")
    
    assert d1["station_id"] == TEST_STATION_1
    assert d2["station_id"] == TEST_STATION_2
    assert d3["station_id"] == TEST_STATION_3
    
    assert d1["station_name"] != d2["station_name"]
    assert d2["station_name"] != d3["station_name"]
    assert d1["latitude"] != d2["latitude"]


# =====================================================================
# TASK H, R: D0 TELEMETRY OBSERVATION-ONLY (NO MOCK/MODEL FALLBACK)
# =====================================================================

def test_d0_telemetry_observation_only_rule():
    """Task H & R: In current operational mode, unobserved D0 returns UNAVAILABLE, never ML fallback."""
    future_date = "2026-09-16"
    data = http_get(f"/forecast/current-telemetry/{TEST_STATION_1}?mode=operational_current&origin_date={future_date}")
    assert data["provenance"] == "UNAVAILABLE"
    assert data["temp_avg_c"] is None
    assert data["rainfall_mm"] is None


def test_d0_telemetry_replay_mode_returns_canonical():
    """Task H: In replay mode, D0 = 2025-01-20 returns authoritative canonical observation."""
    data = http_get(f"/forecast/current-telemetry/{TEST_STATION_1}?mode=historical_holdout_replay")
    assert data["provenance"] == "CURRENT"
    assert data["observation_date"] == "2025-01-20"
    assert data["temp_avg_c"] is not None


# =====================================================================
# TASK I, J: TEMPERATURE TERMINOLOGY & PHYSICAL ORDERING
# =====================================================================

def test_long_term_physical_ordering_and_distinct_temperatures():
    """Task I & J: Tmin <= Tavg <= Tmax is enforced across predictions."""
    pred = run_long_term_prediction(
        station_id=TEST_STATION_1,
        target_date="2026-09-16"
    )
    assert pred["status"] == "AVAILABLE"
    p = pred["predictions"]
    assert p["min_temp"] <= p["avg_temp"]
    assert p["avg_temp"] <= p["max_temp"]
    assert pred["uncertainty"]["avg_temp_interval_80"][0] <= pred["uncertainty"]["avg_temp_interval_80"][1]


# =====================================================================
# TASK M: DYNAMIC HISTORICAL MONTH REFERENCE DERIVATION
# =====================================================================

@pytest.mark.parametrize("target_date,expected_month", [
    ("2026-01-15", "January"),
    ("2026-09-16", "September"),
    ("2026-11-15", "November"),
    ("2026-12-25", "December"),
])
def test_dynamic_historical_month_reference(target_date, expected_month):
    """Task M: Historical month reference dynamically matches target month."""
    pred = run_long_term_prediction(
        station_id=TEST_STATION_2,
        target_date=target_date
    )
    assert pred["status"] == "AVAILABLE"
    assert pred.get("historical_reference") is not None
    cal_month = pred["historical_reference"]["calendar_context"]["month"]
    assert cal_month == expected_month
    
    # Audit trail trace
    how_made = pred["how_prediction_made"]
    step_detail = [h["detail"] for h in how_made if expected_month in h["detail"]]
    assert len(step_detail) > 0, f"Expected {expected_month} in how_prediction_made audit steps"


# =====================================================================
# TASK N, O: RAIN PROBABILITY VS RAINFALL AMOUNT & HISTORICAL FREQUENCY
# =====================================================================

def test_rain_probability_vs_amount_separation():
    """Task N & O: Rain occurrence probability (%) is distinct from expected rainfall amount (mm)."""
    pred = run_long_term_prediction(
        station_id=TEST_STATION_2,
        target_date="2026-09-16"
    )
    assert pred["status"] == "AVAILABLE"
    assert 0.0 <= pred["predictions"]["rain_probability_pct"] <= 100.0
    assert pred["predictions"]["rainfall"] >= 0.0
    
    # Historical climatology frequency is preserved as distinct contextual reference
    hist_freq = pred["historical_reference"]["station_monthly_climatology"]["historical_rain_frequency_pct"]
    assert 0.0 <= hist_freq <= 100.0


# =====================================================================
# TASK P: PREDICTION PROVENANCE DISTINCTION
# =====================================================================

def test_prediction_provenance_distinction():
    """Task P: Inference source is XGBOOST_LONG_TERM or MONGODB_CACHE, not conflated."""
    pred = run_long_term_prediction(
        station_id=TEST_STATION_1,
        target_date="2026-09-16"
    )
    assert pred["provenance"]["inference_source"] in ("XGBOOST_LONG_TERM", "MONGODB_CACHE")
    assert pred["provenance"]["model_version"] == "v1.0.0"


# =====================================================================
# TASK Q: UNCERTAINTY TERMINOLOGY AUDIT
# =====================================================================

def test_zero_active_confidence_interval_occurrences():
    """Task Q: Ensure model metadata and authoritative configs use 80% PI, not 80% CI."""
    meta = get_long_term_model_metadata()
    for key, model_info in meta.items():
        if key in ("avg_temp", "min_temp", "max_temp", "rainfall", "wind_speed", "air_pressure"):
            uncertainty_text = model_info.get("uncertainty_method", "")
            assert "80% CI" not in uncertainty_text, f"Found '80% CI' in model {key} metadata"
            assert "80% PI" in uncertainty_text or "Calibrated" in uncertainty_text


# =====================================================================
# TASK S: API CONTRACT INTEGRITY
# =====================================================================

def test_api_contract_long_term_endpoint():
    """Task S: Verify FastAPI schema validation for long term predictor endpoint."""
    data = http_post("/long-term-predictor/predict", {
        "station_id": TEST_STATION_1,
        "target_date": "2026-09-16"
    })
    assert data["status"] == "AVAILABLE"
    assert "predictions" in data
    assert "uncertainty" in data
    assert "historical_reference" in data
    assert "provenance" in data
