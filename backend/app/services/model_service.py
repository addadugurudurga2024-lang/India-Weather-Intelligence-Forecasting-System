"""Model registry and performance service."""

import json
from typing import Dict, Any
from backend.app.config import settings


def get_model_registry_info() -> Dict[str, Any]:
    """Returns authoritative model registry and baseline metrics."""
    metrics_path = settings.PHASE3_METRICS_PATH
    p3_metrics = {}
    if metrics_path.exists():
        with open(metrics_path, "r", encoding="utf-8") as f:
            p3_metrics = json.load(f)

    return {
        "authoritative_phase3_metrics": p3_metrics,
        "phase7_multi_horizon_models_count": 84,
        "phase9_long_term_models_count": 7,
        "models": [
            {
                "phase": "Phase 3",
                "architecture": "Ridge, Random Forest, XGBoost Baseline",
                "total_models": 7,
                "targets": ["temp_avg", "temp_min", "temp_max", "rainfall", "rain_cls", "wind_speed", "air_pressure"],
                "description": "Baseline model benchmark from canonical 2015-2025 dataset.",
            },
            {
                "phase": "Phase 7",
                "architecture": "Multi-Horizon Direct XGBoost Regressors & Classifiers (H1..H12)",
                "total_models": 84,
                "targets": ["temp", "temp_min", "temp_max", "rain_cls", "rain_amt", "wind", "pres"],
                "description": "Short-term direct multi-horizon operational forecasting models covering T+1 through T+12.",
            },
            {
                "phase": "Phase 9",
                "architecture": "Climatological Harmonics + Regional Climatology XGBoost",
                "total_models": 7,
                "targets": ["avg_temp", "min_temp", "max_temp", "rain_amt", "rain_cls", "wind_spd", "air_pres"],
                "description": "Extended long-term date prediction models with empirical 80% prediction intervals.",
            }
        ]
    }
