"""
Phase 9 Export Frontend Artifacts
Bundles the 413 station climatology database, model metadata, benchmarks, and uncertainty intervals
into a lightweight, zero-latency authoritative JSON for the frontend React application.
"""

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("export_frontend_artifacts")

PROJECT_ROOT = Path("d:/weather_forcasting")
CLIMATOLOGY_PATH = PROJECT_ROOT / "phase9_long_term_predictor" / "data" / "authoritative_station_climatology.json"
METADATA_PATH = PROJECT_ROOT / "phase9_long_term_predictor" / "data" / "phase9_models_metadata.json"
METRICS_PATH = PROJECT_ROOT / "phase9_long_term_predictor" / "data" / "model_evaluation_metrics.json"
STATIONS_CLEAN_PATH = PROJECT_ROOT / "frontend" / "src" / "data" / "authoritativeStations.json"

FE_OUT = PROJECT_ROOT / "frontend" / "src" / "data" / "authoritativeLongTermPredictorData.json"
P9_OUT = PROJECT_ROOT / "phase9_long_term_predictor" / "data" / "authoritativeLongTermPredictorData.json"


def main():
    logger.info("Loading climatology, metadata, and clean stations registry...")
    with open(CLIMATOLOGY_PATH, "r", encoding="utf-8") as f:
        climatology = json.load(f)

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        models_meta = json.load(f)

    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    with open(STATIONS_CLEAN_PATH, "r", encoding="utf-8") as f:
        clean_stations = json.load(f)

    clean_stn_map = {s["station_id"]: s for s in clean_stations}

    # Ensure station names in climatology are clean UTF-8
    for stn_id, data in climatology.items():
        if stn_id in clean_stn_map:
            cs = clean_stn_map[stn_id]
            data["station_name"] = cs["station_name"]
            data["district"] = cs["district"]
            data["state"] = cs["state"]

    payload = {
        "metadata": {
            "title": "Phase 9 Long-Term Weather Predictor Authoritative Data Bundle",
            "version": "v1.0.0",
            "phase": "Phase 9 Long-Term Weather Predictor",
            "supported_date_range": {
                "min_date": "2025-01-01",
                "max_date": "2027-12-31"
            },
            "total_stations_available": len(climatology),
            "targets_supported": [
                "avg_temp",
                "min_temp",
                "max_temp",
                "rainfall",
                "rain_probability",
                "wind_speed",
                "air_pressure"
            ],
            "dataset_hash": "e6a636777430f078b4d970f9f46e79efcece7f97b67dd186c30a755d2783cd84",
            "training_window": "2015-01-01 to 2023-12-31",
            "validation_window": "2024-01-01 to 2024-12-31",
            "holdout_window": "2025-01-01 to 2025-02-10",
        },
        "model_benchmarks": metrics,
        "models_metadata": models_meta,
        "uncertainty_intervals": {
            "avg_temp_interval_80": [-2.1, 2.2],
            "min_temp_interval_80": [-1.8, 2.8],
            "max_temp_interval_80": [-2.7, 2.8],
            "rainfall_interval_80": [-7.3, 5.1],
            "wind_speed_interval_80": [-2.4, 5.4],
            "air_pressure_interval_80": [-3.0, 2.9],
            "method": "Empirical residual quantiles from 2024 out-of-time walk-forward validation"
        },
        "station_climatology": climatology
    }

    logger.info(f"Saving bundle to {FE_OUT} and {P9_OUT}...")
    with open(FE_OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    with open(P9_OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    logger.info("Export completed successfully!")


if __name__ == "__main__":
    main()
