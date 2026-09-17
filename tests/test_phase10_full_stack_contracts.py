"""Phase 10 Full-Stack API Contract & Integration Tests.

Validates the complete FastAPI application contracts, ML inference adapters,
and canonical data synchronization.
"""

import asyncio
import json
from typing import Tuple, Dict, Any, Optional
import pytest
from backend.app.main import app


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
        parsed = json.loads(raw_body.decode("utf-8"))
    except Exception:
        parsed = {"raw": raw_body.decode("utf-8", errors="replace")}

    return status, parsed


def asgi_call(method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any]]:
    """Synchronous wrapper for test execution."""
    return asyncio.run(_asgi_request(method, path, body))


def test_contract_01_health_and_registry():
    """Verify system health endpoint and asset counts."""
    status, res = asgi_call("GET", "/api/v1/health")
    assert status == 200
    assert res["status"] == "HEALTHY"
    assert res["canonical_stations_count"] == 413
    assert res["phase7_models_verified"] == 84
    assert res["phase9_models_verified"] == 7


def test_contract_02_stations_and_geographic_hierarchy():
    """Verify 413 canonical stations listing and State -> District hierarchy."""
    status, res = asgi_call("GET", "/api/v1/stations")
    assert status == 200
    assert res["total_stations"] == 413
    assert len(res["stations"]) == 413

    # Check hierarchy
    status_h, hier = asgi_call("GET", "/api/v1/stations/hierarchy")
    assert status_h == 200
    assert len(hier) >= 25  # All Indian states and UTs

    # Check single station lookup
    sample_id = res["stations"][0]["station_id"]
    status_s, stn = asgi_call("GET", f"/api/v1/stations/{sample_id}")
    assert status_s == 200
    assert stn["station_id"] == sample_id
    assert "station_name" in stn
    assert "elevation_m" in stn


def test_contract_03_historical_analytics_and_timeseries():
    """Verify historical summary and timeseries retrieval from canonical data."""
    stn_id = "rajahmundry_rjnagaram_17.1104_81.8182_46m"
    status, summary = asgi_call("GET", f"/api/v1/analytics/summary/{stn_id}")
    assert status == 200
    assert summary["station_id"] == stn_id
    assert summary["record_count"] > 0
    assert summary["temp_avg_mean"] is not None
    assert summary["temp_min_record"] <= summary["temp_max_record"]

    status_ts, ts = asgi_call("GET", f"/api/v1/analytics/timeseries/{stn_id}?limit=15")
    assert status_ts == 200
    assert ts["total_points"] == 15
    assert len(ts["data"]) == 15
    assert "temp_avg" in ts["data"][0]


def test_contract_04_operational_forecast_and_timeline():
    """Verify 25-day timeline and T+1..T+12 multi-horizon direct XGBoost routing."""
    stn_id = "rajahmundry_rjnagaram_17.1104_81.8182_46m"

    # Multi-horizon forecast
    status_fc, fc = asgi_call("GET", f"/api/v1/forecast/multi-horizon/{stn_id}")
    assert status_fc == 200
    assert len(fc["horizons"]) == 12
    for h in fc["horizons"]:
        assert 1 <= h["horizon"] <= 12
        assert h["temp_min_c"] <= h["temp_avg_c"] <= h["temp_max_c"] + 0.1
        assert h["rainfall_mm"] >= 0.0
        assert 0.0 <= h["rain_probability"] <= 1.0
        assert h["models_used"]["temp"] == f"xgb_temp_h{h['horizon']}.json"

    # 25-day timeline
    status_tl, tl = asgi_call("GET", f"/api/v1/forecast/25day-timeline/{stn_id}")
    assert status_tl == 200
    assert tl["timeline_days_count"] == 25
    
    d0_day = next(d for d in tl["timeline"] if d["day_offset"] == 0)
    assert d0_day["provenance"] in ("CURRENT", "UNAVAILABLE")
    assert d0_day.get("model_name") is None, "D0 must have zero model fallback"


def test_contract_05_ai_weather_intelligence():
    """Verify grounded Q&A, unsupported topic guardrails, and executive summaries."""
    stn_id = "rajahmundry_rjnagaram_17.1104_81.8182_46m"

    # Grounded query
    status_q, ans = asgi_call("POST", "/api/v1/intelligence/query", {
        "station_id": stn_id,
        "question": "Will rain occur in the next 3 days?",
    })
    assert status_q == 200
    assert len(ans["answer"]) > 10

    # Guardrail test: reject unsupported topic
    status_rej, ans_rej = asgi_call("POST", "/api/v1/intelligence/query", {
        "station_id": stn_id,
        "question": "What is the humidity today?",
    })
    assert status_rej == 200
    assert ans_rej["intent"] == "UNSUPPORTED_TOPIC"
    assert "Data unavailable" in ans_rej["answer"]

    # Summary
    status_sum, summary = asgi_call("GET", f"/api/v1/intelligence/summary/{stn_id}")
    assert status_sum == 200
    assert summary["grounding_verified"] is True


def test_contract_06_long_term_predictor():
    """Verify Phase 9 Long-Term Predictor 7 targets, 80% intervals, and historical reference."""
    stn_id = "rajahmundry_rjnagaram_17.1104_81.8182_46m"
    status, pred = asgi_call("POST", "/api/v1/long-term-predictor/predict", {
        "station_id": stn_id,
        "target_date": "2026-11-15",
    })
    assert status == 200
    assert pred["status"] == "AVAILABLE"
    assert pred["prediction_date"] == "2026-11-15"

    p = pred["predictions"]
    assert p["min_temp"] <= p["avg_temp"] <= p["max_temp"]
    assert p["rainfall"] >= 0.0
    assert 0.0 <= p["rain_probability_pct"] <= 100.0
    assert p["wind_speed"] >= 0.0
    assert p["air_pressure"] > 500.0

    unc = pred["uncertainty"]
    assert unc["rainfall_interval_80"][0] >= 0.0
    assert unc["wind_speed_interval_80"][0] >= 0.0
    assert unc["avg_temp_interval_80"][0] <= unc["avg_temp_interval_80"][1]

    hist = pred["historical_reference"]
    assert hist["calendar_context"]["selected_date"] == "2026-11-15"


def test_contract_07_structured_error_handling():
    """Verify API structured error behavior on invalid inputs."""
    # Invalid station
    status, err = asgi_call("GET", "/api/v1/stations/invalid_station_xyz")
    assert status == 404
    assert "not found" in err["detail"]

    # Out of range date
    status_date, err_date = asgi_call("POST", "/api/v1/long-term-predictor/predict", {
        "station_id": "rajahmundry_rjnagaram_17.1104_81.8182_46m",
        "target_date": "2035-01-01",
    })
    assert status_date == 400
    assert "outside the validated" in err_date["detail"]

    # Malformed body
    status_val, err_val = asgi_call("POST", "/api/v1/intelligence/query", {"missing_fields": True})
    assert status_val == 422
    assert err_val["error"] == "Validation Error"
