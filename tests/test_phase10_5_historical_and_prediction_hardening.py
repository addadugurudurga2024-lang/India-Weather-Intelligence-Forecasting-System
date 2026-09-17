"""Focused tests for Phase 10.5 Historical Data Retrieval + Long-Term Prediction Integrity Hardening."""

import asyncio
import json
from typing import Tuple, Dict, Any, Optional
import pytest
from backend.app.main import app
from phase9_long_term_predictor.services.long_term_predictor_engine import predict_long_term
from backend.app.services.data_service import (
    get_station_by_id,
    get_scoped_observations,
    get_scoped_timeseries,
    load_stations,
)


async def _asgi_request(
    method: str,
    path_with_query: str,
    body: Optional[Dict[str, Any]] = None
) -> Tuple[int, Dict[str, Any]]:
    """Helper executing ASGI requests directly against the FastAPI app instance."""
    parts = path_with_query.split("?")
    path = parts[0]
    qs = parts[1].encode("utf-8") if len(parts) > 1 else b""
    
    sent = []
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "raw_path": path.encode("utf-8"),
        "query_string": qs,
        "headers": [(b"content-type", b"application/json")],
    }
    body_bytes = json.dumps(body).encode("utf-8") if body is not None else b""

    async def receive():
        return {"type": "http.request", "body": body_bytes, "more_body": False}

    async def send(message):
        sent.append(message)

    await app(scope, receive, send)

    status = next(s["status"] for s in sent if s["type"] == "http.response.start")
    raw_body = b"".join(s.get("body", b"") for s in sent if s["type"] == "http.response.body")

    try:
        parsed_body = json.loads(raw_body.decode("utf-8")) if raw_body else {}
    except Exception:
        parsed_body = {"raw": raw_body.decode("utf-8", errors="ignore")}

    return status, parsed_body


def asgi_call(method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any]]:
    """Synchronous wrapper for test execution."""
    return asyncio.run(_asgi_request(method, path, body))


def test_station_id_resolution():
    """Verify authoritative station ID resolution for required cases."""
    raj = get_station_by_id("rajahmundry_rjnagaram_17.1104_81.8182_46m")
    assert raj is not None
    assert raj["state"] == "AP"
    assert raj["district"] == "East Godavari"
    assert "Rajahmundry" in raj["station_name"]

    renta = get_station_by_id("rentachintala_16.5500_79.5500_104m")
    assert renta is not None
    assert renta["state"] == "AP"
    assert renta["district"] == "Guntur"
    assert renta["station_name"] == "Rentachintala"

    all_stns = load_stations()
    assert len(all_stns) == 413


def test_scoped_observations_ap_guntur():
    """Verify Case A: AP Guntur scoped retrieval."""
    status, data = asgi_call("GET", "/api/v1/analytics/observations?state=AP&district=Guntur&limit=10")
    assert status == 200
    assert data["total_records"] > 0
    for rec in data["data"]:
        assert rec["state"] == "AP"
        assert rec["district"] == "Guntur"
        assert rec["avg_temp"] is not None


def test_scoped_timeseries_ap_guntur():
    """Verify Case A: AP Guntur scoped timeseries is non-empty."""
    status, data = asgi_call("GET", "/api/v1/analytics/scoped-timeseries?state=AP&district=Guntur&limit=30")
    assert status == 200
    assert data["total_points"] > 0
    assert len(data["data"]) > 0


def test_station_explorer_recent_observations_rajahmundry():
    """Verify Case B: Rajahmundry recent historical telemetry records."""
    status, data = asgi_call("GET", "/api/v1/analytics/station-history/rajahmundry_rjnagaram_17.1104_81.8182_46m?limit=15")
    assert status == 200
    assert data["total_records"] > 0
    records = data["data"]
    assert len(records) >= 10
    # First record should be the most recent (2025-02-10)
    assert records[0]["date_of_record"] == "2025-02-10"
    assert records[0]["avg_temp"] == 26.6


def test_scoped_analytics_tamil_nadu():
    """Verify Case C: Tamil Nadu state-level scope with 30 stations."""
    status, data = asgi_call("GET", "/api/v1/analytics/observations?state=TN&limit=50")
    assert status == 200
    assert data["total_records"] > 0
    for rec in data["data"]:
        assert rec["state"] == "TN"

    ts_status, ts_data = asgi_call("GET", "/api/v1/analytics/scoped-timeseries?state=TN&limit=30")
    assert ts_status == 200
    assert ts_data["total_points"] > 0
    assert len(ts_data["data"]) > 0


def test_rainfall_null_versus_zero_semantics():
    """Verify that rainfall 0.0 is observed dry day and null is preserved as missing."""
    obs = get_scoped_observations(state="TN", limit=500)
    has_dry_zero = any(o["rainfall"] == 0.0 for o in obs)
    has_rainy = any(o["rainfall"] is not None and o["rainfall"] > 0 for o in obs)
    assert has_dry_zero, "Expected verified dry days with 0.0 mm"
    assert has_rainy, "Expected active rainy days with >0.0 mm"


def test_long_term_prediction_inference_provenance():
    """Verify genuine XGBoost inference across seasonal dates."""
    raj_sep = predict_long_term("rajahmundry_rjnagaram_17.1104_81.8182_46m", "2026-09-15")
    assert raj_sep["status"] == "AVAILABLE"
    # In September (monsoon), rain probability is high (>80%)
    assert raj_sep["predictions"]["rain_probability_pct"] > 75.0

    raj_nov = predict_long_term("rajahmundry_rjnagaram_17.1104_81.8182_46m", "2026-11-15")
    assert raj_nov["status"] == "AVAILABLE"
    # In November, rain probability is distinct and much lower
    assert raj_nov["predictions"]["rain_probability_pct"] < 60.0
    assert raj_nov["predictions"]["rain_probability_pct"] != raj_nov["historical_reference"]["station_monthly_climatology"]["historical_rain_frequency_pct"]


def test_long_term_prediction_physical_ordering():
    """Verify physical temperature constraint T_min <= T_avg <= T_max."""
    for dt_str in ["2026-01-15", "2026-05-15", "2026-07-20", "2026-11-15"]:
        res = predict_long_term("rajahmundry_rjnagaram_17.1104_81.8182_46m", dt_str)
        p = res["predictions"]
        assert p["min_temp"] <= p["avg_temp"] <= p["max_temp"]
        assert p["rainfall"] >= 0.0
        assert 0.0 <= p["rain_probability"] <= 1.0
