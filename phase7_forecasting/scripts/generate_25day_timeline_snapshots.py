"""
Generates authoritative 25-day timeline development seed payloads for key representative stations.
Outputs to:
- phase7_forecasting/data/authoritative25DayTimeline.json
- frontend/src/data/authoritative25DayTimeline.json
"""

import json
import logging
from pathlib import Path
import pandas as pd

from operational_ingestion_service import build_operational_timeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("generate_25day_timeline_snapshots")

PROJECT_ROOT = Path("d:/weather_forcasting")
CANONICAL_DATA_PATH = PROJECT_ROOT / "phase2_canonical" / "outputs" / "features_engineered.parquet"
EVAL_SUMMARY_PATH = PROJECT_ROOT / "phase7_forecasting" / "data" / "phase7_multi_horizon_evaluation_summary.json"
OUTPUT_PATH = PROJECT_ROOT / "phase7_forecasting" / "data" / "authoritative25DayTimeline.json"
FE_OUTPUT_PATH = PROJECT_ROOT / "frontend" / "src" / "data" / "authoritative25DayTimeline.json"

def main():
    logger.info("Loading canonical parquet, station registry, and evaluation summary...")
    stations_seed_path = PROJECT_ROOT / "frontend" / "src" / "data" / "authoritativeStations.json"
    with open(stations_seed_path, "r", encoding="utf-8") as f:
        stations_registry = json.load(f)

    stn_ids = [s["station_id"] for s in stations_registry]
    logger.info(f"Loaded {len(stn_ids)} canonical stations to generate.")

    df_canonical = pd.read_parquet(CANONICAL_DATA_PATH)
    df_canonical["date_of_record"] = pd.to_datetime(df_canonical["date_of_record"])

    with open(EVAL_SUMMARY_PATH, "r", encoding="utf-8") as f:
        eval_summary = json.load(f)

    timelines = {}

    for idx, stn_id in enumerate(stn_ids, 1):
        if idx % 50 == 0 or idx == 1 or idx == len(stn_ids):
            logger.info(f"[{idx}/{len(stn_ids)}] Generating 25-day timelines for: {stn_id}...")

        # 1. Audited historical holdout anchor (2025-01-20)
        hist_timeline = build_operational_timeline(
            station_id=stn_id,
            origin_date="2025-01-20",
            df_canonical=df_canonical,
            eval_summary=eval_summary,
        )

        # 2. Operational current anchor (2026-09-13) with fast model-derived context
        live_timeline = build_operational_timeline(
            station_id=stn_id,
            origin_date="2026-09-13",
            df_canonical=None,
            eval_summary=eval_summary,
            skip_external_api=True,
        )

        timelines[stn_id] = {
            "historical_holdout_replay": hist_timeline,
            "operational_current": live_timeline,
        }

    payload = {
        "metadata": {
            "title": "Authoritative 25-Day Operational Weather Timelines",
            "phase": "Phase 8.5 Operational Hardening",
            "generated_at": "2026-09-13T17:30:00Z",
            "stations_available": list(timelines.keys()),
            "total_stations_available": len(timelines),
            "default_station_id": "new_delhi_safdarjung_28.5833_77.2000_211m",
            "primary_mode": "historical_holdout_replay",
        },
        "stations": timelines,
    }

    logger.info("Saving authoritative 25-day timeline artifacts...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    with open(FE_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    logger.info("25-day timeline generation complete!")

if __name__ == "__main__":
    main()
