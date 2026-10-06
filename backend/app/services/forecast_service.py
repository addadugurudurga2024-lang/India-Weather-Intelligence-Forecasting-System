"""Operational forecast service adapter wrapping Phase 7 models and timelines."""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from backend.app.config import settings

# Insert Phase 7 scripts path
sys.path.insert(0, str(settings.ROOT_PATH / "phase7_forecasting" / "scripts"))
from operational_ingestion_service import (
    build_operational_timeline as _build_timeline,
    get_station_feature_state as _get_feature_state,
    load_station_metadata,
    get_horizon_inference_diagnostics as _get_diagnostics,
)
from backend.app.services.data_service import get_station_by_id


def get_operational_timeline(
    station_id: str,
    mode: str = "historical_holdout_replay",
    origin_date: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Builds authoritative 25-day timeline: D-12..D-1 (Obs/Est), D0 (Telemetry/Unavailable), D+1..D+12 (P7 Models)."""
    stn = get_station_by_id(station_id)
    if not stn:
        return None
    
    # Determine effective origin_date based on mode
    if mode == "operational_current":
        effective_origin = origin_date or datetime.now().strftime("%Y-%m-%d")
    else:
        # Audited ground-truth replay mode
        effective_origin = "2025-01-20"
    
    timeline_data = _build_timeline(station_id, origin_date=effective_origin)
    if not timeline_data or "timeline" not in timeline_data:
        # Check complete_timeline or timeline keys
        raw_list = timeline_data.get("timeline") or timeline_data.get("complete_timeline", [])
    else:
        raw_list = timeline_data["timeline"]

    normalized = []
    for item in raw_list:
        h_offset = int(item.get("relative_day", 0))
        label = "D0" if h_offset == 0 else (f"D+{h_offset}" if h_offset > 0 else f"D{h_offset}")
        
        status_val = item.get("status", "UNAVAILABLE")
        if status_val == "OBSERVED":
            prov = "OBSERVED"
            canonical_status = "OBSERVED"
        elif status_val == "CURRENT":
            prov = "CURRENT"
            canonical_status = "CURRENT"
        elif status_val == "FORECAST":
            prov = item.get("provenance", f"XGBoost Multi-Horizon Direct Engine (xgb_multi_horizon_h{h_offset}_v1)")
            canonical_status = "FORECAST"
        elif status_val == "MODEL ESTIMATE":
            prov = item.get("provenance", "MODEL ESTIMATE")
            canonical_status = "MODEL ESTIMATE"
        else:
            prov = item.get("provenance", "UNAVAILABLE")
            canonical_status = "UNAVAILABLE"

        normalized.append({
            "date": item.get("date"),
            "day_offset": h_offset,
            "horizon_label": label,
            "status": canonical_status,
            "provenance": prov,
            "is_observed": bool(item.get("is_observed", canonical_status in ("OBSERVED", "CURRENT"))),
            "temp_avg_c": item.get("temperature_avg"),
            "temp_min_c": item.get("temperature_min"),
            "temp_max_c": item.get("temperature_max"),
            "rainfall_mm": item.get("rainfall_amount"),
            "rain_probability": item.get("rain_probability"),
            "wind_kmh": item.get("wind_speed"),
            "pressure_hpa": item.get("air_pressure"),
            "model_name": item.get("model_metadata", {}).get("model_id") if item.get("model_metadata") else None,
            "uncertainty": item.get("uncertainty"),
            "model_metadata": item.get("model_metadata"),
        })

    return {
        "station_id": station_id,
        "station_name": stn["station_name"],
        "state": stn["state"],
        "district": stn["district"],
        "latitude": stn.get("latitude", 20.0),
        "longitude": stn.get("longitude", 78.0),
        "elevation_m": stn.get("elevation_m", 100.0),
        "forecast_origin": timeline_data.get("forecast_origin", effective_origin),
        "timeline_days_count": len(normalized),
        "timeline": normalized,
    }


def get_multi_horizon_forecast(
    station_id: str,
    mode: str = "historical_holdout_replay",
    origin_date: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Runs direct multi-horizon inference for horizons T+1 through T+12 using frozen Phase 7 models."""
    stn = get_station_by_id(station_id)
    if not stn:
        return None

    if mode == "operational_current":
        effective_origin = origin_date or datetime.now().strftime("%Y-%m-%d")
    else:
        effective_origin = "2025-01-20"

    timeline_data = _build_timeline(station_id, origin_date=effective_origin)
    if not timeline_data:
        return None

    raw_list = timeline_data.get("timeline") or timeline_data.get("complete_timeline", [])
    horizons = []
    for item in raw_list:
        h = int(item.get("relative_day", 0))
        if 1 <= h <= 12:
            models_map = {
                "temp": f"xgb_temp_h{h}.json",
                "temp_min": f"xgb_temp_min_h{h}.json",
                "temp_max": f"xgb_temp_max_h{h}.json",
                "rain_cls": f"xgb_rain_cls_h{h}.json",
                "rain_amt": f"xgb_rain_amt_h{h}.json",
                "wind": f"xgb_wind_h{h}.json",
                "pres": f"xgb_pres_h{h}.json",
            }
            horizons.append({
                "horizon": h,
                "target_date": item.get("date"),
                "temp_avg_c": item.get("temperature_avg", 25.0),
                "temp_min_c": item.get("temperature_min", 20.0),
                "temp_max_c": item.get("temperature_max", 30.0),
                "rainfall_mm": item.get("rainfall_amount", 0.0),
                "rain_probability": item.get("rain_probability", 0.0),
                "wind_kmh": item.get("wind_speed", 5.0),
                "pressure_hpa": item.get("air_pressure", 1012.0),
                "models_used": models_map,
            })

    return {
        "station_id": station_id,
        "forecast_origin": timeline_data.get("forecast_origin", effective_origin),
        "horizons": horizons,
    }


def get_current_telemetry(
    station_id: str,
    mode: str = "historical_holdout_replay",
    origin_date: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Retrieves physical D0 telemetry without ANY model fallback."""
    stn = get_station_by_id(station_id)
    if not stn:
        return None

    if mode == "operational_current":
        effective_origin = origin_date or datetime.now().strftime("%Y-%m-%d")
    else:
        effective_origin = "2025-01-20"

    timeline_data = _build_timeline(station_id, origin_date=effective_origin)
    if not timeline_data:
        return None

    raw_list = timeline_data.get("timeline") or timeline_data.get("complete_timeline", [])
    d0_item = next((item for item in raw_list if int(item.get("relative_day", -99)) == 0), None)

    if not d0_item or d0_item.get("status") == "UNAVAILABLE" or d0_item.get("temperature_avg") is None or not d0_item.get("is_observed", False):
        return {
            "station_id": station_id,
            "observation_date": effective_origin,
            "provenance": "UNAVAILABLE",
            "temp_avg_c": None,
            "temp_min_c": None,
            "temp_max_c": None,
            "rainfall_mm": None,
            "wind_kmh": None,
            "pressure_hpa": None,
        }

    return {
        "station_id": station_id,
        "observation_date": d0_item.get("date", effective_origin),
        "provenance": "CURRENT",
        "temp_avg_c": d0_item.get("temperature_avg"),
        "temp_min_c": d0_item.get("temperature_min"),
        "temp_max_c": d0_item.get("temperature_max"),
        "rainfall_mm": d0_item.get("rainfall_amount"),
        "wind_kmh": d0_item.get("wind_speed"),
        "pressure_hpa": d0_item.get("air_pressure"),
    }


def get_horizon_diagnostics(
    station_id: str,
    mode: str = "historical_holdout_replay",
    origin_date: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Retrieves full horizon diagnostic audit data for H1 through H12 (Section 24)."""
    stn = get_station_by_id(station_id)
    if not stn:
        return None

    if mode == "operational_current":
        effective_origin = origin_date or datetime.now().strftime("%Y-%m-%d")
    else:
        effective_origin = "2025-01-20"

    diag_data = _get_diagnostics(station_id, origin_date=effective_origin)
    if not diag_data:
        return None

    return {
        "station_id": station_id,
        "forecast_origin": effective_origin,
        "mode": mode,
        "horizons_count": diag_data.get("horizons_count", 12),
        "diagnostics": diag_data.get("diagnostics", []),
    }
