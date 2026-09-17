"""
Authoritative Python Prediction Engine for Phase 9 Long-Term Weather Predictor
Provides fast, deterministic, cached inference across all 413 canonical stations
and future calendar dates.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import numpy as np
import xgboost as xgb

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("long_term_predictor_engine")

PROJECT_ROOT = Path("d:/weather_forcasting")
CLIMATOLOGY_PATH = PROJECT_ROOT / "phase9_long_term_predictor" / "data" / "authoritative_station_climatology.json"
MODELS_DIR = PROJECT_ROOT / "phase9_long_term_predictor" / "models"
METADATA_PATH = PROJECT_ROOT / "phase9_long_term_predictor" / "data" / "phase9_models_metadata.json"

FEATURE_NAMES = [
    "doy",
    "doy_sin",
    "doy_cos",
    "doy_sin2",
    "doy_cos2",
    "month",
    "season_code",
    "latitude",
    "longitude",
    "elevation",
    "station_hist_avg_temp_mean",
    "station_hist_min_temp_mean",
    "station_hist_max_temp_mean",
    "station_hist_wind_speed_mean",
    "station_hist_air_pressure_mean",
    "station_hist_rain_frequency",
    "station_month_avg_temp_mean",
    "station_month_avg_temp_std",
    "station_month_min_temp_mean",
    "station_month_max_temp_mean",
    "station_month_wind_speed_mean",
    "station_month_air_pressure_mean",
    "station_month_rain_frequency",
    "station_month_rain_amount_mean",
]

MONTH_SEASONS = {
    1: 0, 2: 0,        # Winter
    3: 1, 4: 1, 5: 1,  # Summer
    6: 2, 7: 2, 8: 2, 9: 2,  # Monsoon
    10: 3, 11: 3, 12: 3      # Post-monsoon
}

SEASON_NAMES = {0: "Winter", 1: "Summer", 2: "Southwest Monsoon", 3: "Post-Monsoon"}

SUPPORTED_MIN_DATE = "2025-01-01"
SUPPORTED_MAX_DATE = "2027-12-31"

# In-memory singletons for fast response
_CLIMATOLOGY: Optional[Dict[str, Any]] = None
_METADATA: Optional[Dict[str, Any]] = None
_MODELS: Dict[str, Any] = {}


def get_climatology() -> Dict[str, Any]:
    global _CLIMATOLOGY
    if _CLIMATOLOGY is None:
        with open(CLIMATOLOGY_PATH, "r", encoding="utf-8") as f:
            _CLIMATOLOGY = json.load(f)
    return _CLIMATOLOGY


def get_metadata() -> Dict[str, Any]:
    global _METADATA
    if _METADATA is None:
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            _METADATA = json.load(f)
    return _METADATA


def get_model(model_id: str, filename: str, is_classifier: bool = False):
    global _MODELS
    if model_id not in _MODELS:
        model_path = MODELS_DIR / filename
        if is_classifier:
            model = xgb.XGBClassifier()
        else:
            model = xgb.XGBRegressor()
        model.load_model(str(model_path))
        _MODELS[model_id] = model
    return _MODELS[model_id]


def build_feature_vector(station_id: str, target_date_str: str) -> Tuple[np.ndarray, Dict[str, Any], Dict[str, Any]]:
    climatology = get_climatology()
    if station_id not in climatology:
        raise ValueError(f"Station ID '{station_id}' is not in authoritative canonical registry.")

    stn_data = climatology[station_id]
    dt = datetime.strptime(target_date_str, "%Y-%m-%d")

    doy = dt.timetuple().tm_yday
    month = dt.month
    season_code = MONTH_SEASONS[month]

    doy_sin = float(np.sin(2 * np.pi * doy / 365.25))
    doy_cos = float(np.cos(2 * np.pi * doy / 365.25))
    doy_sin2 = float(np.sin(4 * np.pi * doy / 365.25))
    doy_cos2 = float(np.cos(4 * np.pi * doy / 365.25))

    ov = stn_data.get("hist_overall", {})
    m_data = stn_data.get("monthly_climatology", {}).get(str(month), {})

    feat_vals = [
        doy,
        doy_sin,
        doy_cos,
        doy_sin2,
        doy_cos2,
        month,
        season_code,
        stn_data["latitude"],
        stn_data["longitude"],
        stn_data["elevation_m"],
        ov.get("avg_temp_mean", 25.0) or 25.0,
        ov.get("min_temp_mean", 20.0) or 20.0,
        ov.get("max_temp_mean", 30.0) or 30.0,
        ov.get("wind_speed_mean", 5.0) or 5.0,
        ov.get("air_pressure_mean", 1010.0) or 1010.0,
        ov.get("rain_frequency", 0.2) or 0.2,
        m_data.get("avg_temp_mean", 25.0) or 25.0,
        m_data.get("avg_temp_std", 1.5) or 1.5,
        m_data.get("min_temp_mean", 20.0) or 20.0,
        m_data.get("max_temp_mean", 30.0) or 30.0,
        m_data.get("wind_speed_mean", 5.0) or 5.0,
        m_data.get("air_pressure_mean", 1010.0) or 1010.0,
        m_data.get("rain_frequency", 0.2) or 0.2,
        m_data.get("rainfall_mean", 0.0) or 0.0,
    ]

    return np.array(feat_vals).reshape(1, -1), stn_data, m_data


def predict_long_term(station_id: str, target_date_str: str) -> Dict[str, Any]:
    """Generates complete long-term weather prediction for a station and future calendar date."""
    # 1. Date range validation
    if target_date_str < SUPPORTED_MIN_DATE or target_date_str > SUPPORTED_MAX_DATE:
        return {
            "status": "UNAVAILABLE",
            "error": f"Selected date {target_date_str} is outside the validated Long-Term Predictor range ({SUPPORTED_MIN_DATE} to {SUPPORTED_MAX_DATE}).",
            "station_id": station_id,
            "prediction_date": target_date_str,
        }

    # 2. Build feature vector & extract reference metadata
    try:
        X, stn_data, m_ref = build_feature_vector(station_id, target_date_str)
    except ValueError as e:
        return {
            "status": "UNAVAILABLE",
            "error": str(e),
            "station_id": station_id,
            "prediction_date": target_date_str,
        }

    dt = datetime.strptime(target_date_str, "%Y-%m-%d")
    month_name = dt.strftime("%B")
    season_name = SEASON_NAMES[MONTH_SEASONS[dt.month]]

    # 3. Model Inference across all 7 targets
    m_temp = get_model("xgb_longterm_temp_v1", "xgb_longterm_temp_v1.json")
    m_min = get_model("xgb_longterm_temp_min_v1", "xgb_longterm_temp_min_v1.json")
    m_max = get_model("xgb_longterm_temp_max_v1", "xgb_longterm_temp_max_v1.json")
    m_rain_amt = get_model("xgb_longterm_rain_amt_v1", "xgb_longterm_rain_amt_v1.json")
    m_rain_cls = get_model("xgb_longterm_rain_cls_v1", "xgb_longterm_rain_cls_v1.json", is_classifier=True)
    m_wind = get_model("xgb_longterm_wind_v1", "xgb_longterm_wind_v1.json")
    m_pres = get_model("xgb_longterm_pressure_v1", "xgb_longterm_pressure_v1.json")

    raw_t_avg = float(m_temp.predict(X)[0])
    raw_t_min = float(m_min.predict(X)[0])
    raw_t_max = float(m_max.predict(X)[0])
    raw_rain_amt = max(0.0, float(m_rain_amt.predict(X)[0]))
    raw_rain_prob = float(m_rain_cls.predict_proba(X)[0, 1])
    raw_wind = max(0.0, float(m_wind.predict(X)[0]))
    raw_pres = float(m_pres.predict(X)[0])

    # 4. Enforce Physical Ordering Constraint: T_min <= T_avg <= T_max
    ordered_temps = sorted([raw_t_min, raw_t_avg, raw_t_max])
    t_min, t_avg, t_max = ordered_temps[0], ordered_temps[1], ordered_temps[2]

    # Round outputs
    t_avg = round(t_avg, 1)
    t_min = round(t_min, 1)
    t_max = round(t_max, 1)
    rain_amt = round(raw_rain_amt, 1)
    rain_prob = round(float(np.clip(raw_rain_prob, 0.0, 1.0)), 3)
    rain_prob_pct = round(rain_prob * 100, 1)
    wind_spd = round(raw_wind, 1)
    air_pres = round(raw_pres, 1)

    # 5. Uncertainty (80% empirical prediction intervals)
    uncertainty = {
        "avg_temp_interval_80": [round(t_avg - 2.1, 1), round(t_avg + 2.2, 1)],
        "min_temp_interval_80": [round(t_min - 1.8, 1), round(t_min + 2.8, 1)],
        "max_temp_interval_80": [round(t_max - 2.7, 1), round(t_max + 2.8, 1)],
        "rainfall_interval_80": [max(0.0, round(rain_amt - 7.3, 1)), round(rain_amt + 5.1, 1)],
        "wind_speed_interval_80": [max(0.0, round(wind_spd - 2.4, 1)), round(wind_spd + 5.4, 1)],
        "air_pressure_interval_80": [round(air_pres - 3.0, 1), round(air_pres + 2.9, 1)],
        "method": "Empirical residual quantiles from 2024 out-of-time walk-forward validation",
    }

    # 6. Historical Reference Used (for transparency & user validation)
    historical_reference = {
        "station_name": stn_data["station_name"],
        "state": stn_data["state"],
        "district": stn_data["district"],
        "elevation_m": stn_data["elevation_m"],
        "latitude": stn_data["latitude"],
        "longitude": stn_data["longitude"],
        "calendar_context": {
            "selected_date": target_date_str,
            "month": month_name,
            "season": season_name,
            "day_of_year": dt.timetuple().tm_yday,
        },
        "station_monthly_climatology": {
            "month": month_name,
            "historical_mean_temp": m_ref.get("avg_temp_mean"),
            "historical_min_temp": m_ref.get("min_temp_mean"),
            "historical_max_temp": m_ref.get("max_temp_mean"),
            "historical_rain_frequency_pct": round(m_ref.get("rain_frequency", 0.0) * 100, 1),
            "historical_mean_rainfall_mm": m_ref.get("rainfall_mean"),
            "historical_mean_wind_kmh": m_ref.get("wind_speed_mean"),
            "historical_mean_pressure_hpa": m_ref.get("air_pressure_mean"),
        },
        "station_overall_climatology": stn_data.get("hist_overall", {}),
    }

    # 7. Step-by-step explainability trace
    pipeline_trace = [
        {"step": 1, "title": "Location Resolved", "detail": f"Station {stn_data['station_name']} ({stn_data['district']}, {stn_data['state']}) at elevation {stn_data['elevation_m']}m."},
        {"step": 2, "title": "Calendar Decomposed", "detail": f"Date {target_date_str} mapped to {month_name} ({season_name}), DOY {dt.timetuple().tm_yday} with sinusoidal harmonics."},
        {"step": 3, "title": "Climatology Retrieved", "detail": f"Retrieved multi-year historical {month_name} baseline: {m_ref.get('avg_temp_mean')}°C avg temp, {round(m_ref.get('rain_frequency', 0.0)*100,1)}% rain frequency."},
        {"step": 4, "title": "Feature Vector Constructed", "detail": "Combined 24 leakage-safe features (harmonics + geographic metadata + historical station climate baselines)."},
        {"step": 5, "title": "Direct Model Inference", "detail": "Evaluated 7 trained XGBoost Phase 9 models (v1.0.0)."},
        {"step": 6, "title": "Physical Consistency & Bounds", "detail": "Applied physical temperature sorting (T_min <= T_avg <= T_max) and non-negative rainfall/wind bounds."},
        {"step": 7, "title": "Uncertainty Quantified", "detail": "Computed empirical 80% prediction intervals from out-of-time historical validation residuals."}
    ]

    return {
        "status": "AVAILABLE",
        "prediction_type": "Long-Term Historical / Seasonal Model Estimate",
        "prediction_date": target_date_str,
        "station_id": station_id,
        "station_name": stn_data["station_name"],
        "state": stn_data["state"],
        "district": stn_data["district"],
        "coordinates": {"latitude": stn_data["latitude"], "longitude": stn_data["longitude"], "elevation_m": stn_data["elevation_m"]},
        "predictions": {
            "avg_temp": t_avg,
            "min_temp": t_min,
            "max_temp": t_max,
            "rainfall": rain_amt,
            "rain_probability": rain_prob,
            "rain_probability_pct": rain_prob_pct,
            "wind_speed": wind_spd,
            "air_pressure": air_pres,
        },
        "uncertainty": uncertainty,
        "historical_reference": historical_reference,
        "how_prediction_made": pipeline_trace,
        "provenance": {
            "models_used": {
                "avg_temp": "xgb_longterm_temp_v1",
                "min_temp": "xgb_longterm_temp_min_v1",
                "max_temp": "xgb_longterm_temp_max_v1",
                "rainfall": "xgb_longterm_rain_amt_v1",
                "rain_binary": "xgb_longterm_rain_cls_v1",
                "wind_speed": "xgb_longterm_wind_v1",
                "air_pressure": "xgb_longterm_pressure_v1",
            },
            "training_window": "2015-01-01 to 2023-12-31 (Canonical 10-Year Panel)",
            "validation_window": "2024-01-01 to 2024-12-31 (Strict Walk-Forward)",
            "source_dataset_sha256": "e6a636777430f078b4d970f9f46e79efcece7f97b67dd186c30a755d2783cd84",
            "physical_ordering_applied": True,
        },
        "limitations": [
            "This prediction represents a long-term model-derived historical/seasonal estimate based on learned historical climatology and calendar patterns.",
            "It is NOT an operational numerical weather prediction and cannot resolve day-to-day synoptic weather fronts beyond the 12-day operational forecasting horizon.",
            "Extreme convective precipitation, cyclones, and unseasonal weather anomalies cannot be predicted months in advance.",
            "Actual physical station observations must be recorded on this date to verify accuracy."
        ]
    }


if __name__ == "__main__":
    # Test example from prompt: 15-Nov-2026 at Rajanagaram
    res = predict_long_term("rajahmundry_rjnagaram_17.1104_81.8182_46m", "2026-11-15")
    print(json.dumps(res, indent=2))
