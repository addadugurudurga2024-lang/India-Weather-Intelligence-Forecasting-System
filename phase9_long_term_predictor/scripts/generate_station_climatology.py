"""
Phase 9 Climatology Generator
Generates leakage-free multi-year and monthly climatological statistics for all 413 stations.
Supports:
1. Training-partition climatology (2015-2023) for leakage-free model training and validation.
2. Production authoritative climatology (2015-2025) for runtime reference context and frontend.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("phase9_climatology")

PROJECT_ROOT = Path("d:/weather_forcasting")
CANONICAL_PARQUET = PROJECT_ROOT / "phase2_canonical" / "outputs" / "canonical_weather_full.parquet"
STATION_METADATA_PATH = PROJECT_ROOT / "phase2_canonical" / "outputs" / "station_metadata.json"
DATA_DIR = PROJECT_ROOT / "phase9_long_term_predictor" / "data"
FE_DATA_DIR = PROJECT_ROOT / "frontend" / "src" / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)
FE_DATA_DIR.mkdir(parents=True, exist_ok=True)


def compute_climatology(df: pd.DataFrame) -> Dict[str, Any]:
    """Computes station-level and station-month climatology from a given dataframe slice."""
    logger.info(f"Computing climatology over {len(df)} records across {df['station_id'].nunique()} stations...")

    # Ensure month is integer 1..12
    df = df.copy()
    if not np.issubdtype(df["date_of_record"].dtype, np.datetime64):
        df["date_of_record"] = pd.to_datetime(df["date_of_record"])
    df["month_num"] = df["date_of_record"].dt.month

    # Derived binary rain flag (strictly where rainfall is observed)
    df["rain_binary"] = np.where(df["rainfall"] >= 0.1, 1.0, np.where(df["rainfall"].notna(), 0.0, np.nan))

    climatology = {}

    # Overall station baseline metrics
    stn_overall = df.groupby("station_id").agg({
        "avg_temp_clean": ["mean", "std"],
        "min_temp_clean": ["mean", "min"],
        "max_temp_clean": ["mean", "max"],
        "wind_speed": ["mean", "std"],
        "air_pressure": ["mean", "std"],
        "rainfall": ["mean", "std", "count"],
        "rain_binary": ["mean"],
        "latitude": "first",
        "longitude": "first",
        "elevation": "first",
        "station_name": "first",
        "state": "first",
        "district": "first",
    })

    # Station-Month metrics
    stn_month = df.groupby(["station_id", "month_num"]).agg({
        "avg_temp_clean": ["mean", "std", "min", "max"],
        "min_temp_clean": ["mean", "min"],
        "max_temp_clean": ["mean", "max"],
        "wind_speed": ["mean", "std"],
        "air_pressure": ["mean", "std"],
        "rainfall": ["mean", "std", lambda x: float(np.nanpercentile(x, 75)) if len(x.dropna()) > 0 else 0.0],
        "rain_binary": ["mean"],
    })

    stn_ids = df["station_id"].unique()
    for stn in stn_ids:
        ov = stn_overall.loc[stn]
        stn_dict = {
            "station_id": stn,
            "station_name": ov[("station_name", "first")],
            "state": ov[("state", "first")],
            "district": ov[("district", "first")],
            "latitude": float(ov[("latitude", "first")]),
            "longitude": float(ov[("longitude", "first")]),
            "elevation_m": float(ov[("elevation", "first")]),
            "hist_overall": {
                "avg_temp_mean": round(float(ov[("avg_temp_clean", "mean")]), 2) if not np.isnan(ov[("avg_temp_clean", "mean")]) else None,
                "min_temp_mean": round(float(ov[("min_temp_clean", "mean")]), 2) if not np.isnan(ov[("min_temp_clean", "mean")]) else None,
                "max_temp_mean": round(float(ov[("max_temp_clean", "mean")]), 2) if not np.isnan(ov[("max_temp_clean", "mean")]) else None,
                "wind_speed_mean": round(float(ov[("wind_speed", "mean")]), 2) if not np.isnan(ov[("wind_speed", "mean")]) else None,
                "air_pressure_mean": round(float(ov[("air_pressure", "mean")]), 2) if not np.isnan(ov[("air_pressure", "mean")]) else None,
                "rain_frequency": round(float(ov[("rain_binary", "mean")]), 4) if not np.isnan(ov[("rain_binary", "mean")]) else 0.0,
                "rainfall_mean": round(float(ov[("rainfall", "mean")]), 2) if not np.isnan(ov[("rainfall", "mean")]) else 0.0,
            },
            "monthly_climatology": {},
        }

        for m in range(1, 13):
            if (stn, m) in stn_month.index:
                m_row = stn_month.loc[(stn, m)]
                stn_dict["monthly_climatology"][str(m)] = {
                    "avg_temp_mean": round(float(m_row[("avg_temp_clean", "mean")]), 2) if not np.isnan(m_row[("avg_temp_clean", "mean")]) else None,
                    "avg_temp_std": round(float(m_row[("avg_temp_clean", "std")]), 2) if not np.isnan(m_row[("avg_temp_clean", "std")]) else 1.5,
                    "min_temp_mean": round(float(m_row[("min_temp_clean", "mean")]), 2) if not np.isnan(m_row[("min_temp_clean", "mean")]) else None,
                    "max_temp_mean": round(float(m_row[("max_temp_clean", "mean")]), 2) if not np.isnan(m_row[("max_temp_clean", "mean")]) else None,
                    "wind_speed_mean": round(float(m_row[("wind_speed", "mean")]), 2) if not np.isnan(m_row[("wind_speed", "mean")]) else None,
                    "air_pressure_mean": round(float(m_row[("air_pressure", "mean")]), 2) if not np.isnan(m_row[("air_pressure", "mean")]) else None,
                    "rain_frequency": round(float(m_row[("rain_binary", "mean")]), 4) if not np.isnan(m_row[("rain_binary", "mean")]) else 0.0,
                    "rainfall_mean": round(float(m_row[("rainfall", "mean")]), 2) if not np.isnan(m_row[("rainfall", "mean")]) else 0.0,
                    "rainfall_p75": round(float(m_row[("rainfall", "<lambda_0>")]), 2) if not np.isnan(m_row[("rainfall", "<lambda_0>")]) else 0.0,
                }
            else:
                # Fallback to overall station metrics if specific month is missing
                stn_dict["monthly_climatology"][str(m)] = {
                    "avg_temp_mean": stn_dict["hist_overall"]["avg_temp_mean"],
                    "avg_temp_std": 2.0,
                    "min_temp_mean": stn_dict["hist_overall"]["min_temp_mean"],
                    "max_temp_mean": stn_dict["hist_overall"]["max_temp_mean"],
                    "wind_speed_mean": stn_dict["hist_overall"]["wind_speed_mean"],
                    "air_pressure_mean": stn_dict["hist_overall"]["air_pressure_mean"],
                    "rain_frequency": stn_dict["hist_overall"]["rain_frequency"],
                    "rainfall_mean": stn_dict["hist_overall"]["rainfall_mean"],
                    "rainfall_p75": 0.0,
                }

        climatology[stn] = stn_dict

    return climatology


def main():
    logger.info("Loading canonical weather dataset...")
    df = pd.read_parquet(CANONICAL_PARQUET)
    df["date_of_record"] = pd.to_datetime(df["date_of_record"])

    # 1. Training partition climatology (<= 2023) to prevent evaluation leakage
    logger.info("Computing training climatology (2015-2023)...")
    train_df = df[df["date_of_record"].dt.year <= 2023]
    train_climatology = compute_climatology(train_df)

    train_out_path = DATA_DIR / "station_climatology_train_2015_2023.json"
    with open(train_out_path, "w", encoding="utf-8") as f:
        json.dump(train_climatology, f, indent=2)
    logger.info(f"Saved training climatology to {train_out_path}")

    # 2. Authoritative full climatology (2015-2025) for production runtime
    logger.info("Computing authoritative full climatology (2015-2025)...")
    full_climatology = compute_climatology(df)

    full_out_path = DATA_DIR / "authoritative_station_climatology.json"
    with open(full_out_path, "w", encoding="utf-8") as f:
        json.dump(full_climatology, f, indent=2)
    logger.info(f"Saved authoritative climatology to {full_out_path}")


if __name__ == "__main__":
    main()
