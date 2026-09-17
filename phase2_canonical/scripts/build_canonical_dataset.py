"""
Phase 2: Build Canonical Datasets & Station Metadata Registry
Outputs:
- canonical_weather_full.parquet (2015-2025, 968,849 rows)
- canonical_weather_forecasting.parquet (2021-2025, 604,155 rows)
- station_metadata.json (414 physical stations with coordinates, dates, and administrative boundaries)
- data_dictionary.json
"""

import json
import logging
import sys
from pathlib import Path
from typing import Tuple
import pandas as pd

sys.path.append(str(Path(__file__).parent))

from config import (
    CANONICAL_FULL_PATH,
    CANONICAL_FORECAST_PATH,
    STATION_REGISTRY_PATH,
    DATA_DICTIONARY_PATH
)
from clean_and_standardize import clean_and_tag_dataset

logger = logging.getLogger("phase2_canonical.builder")

def build_canonical_artifacts() -> Tuple[pd.DataFrame, pd.DataFrame]:
    logger.info("Generating clean canonical dataframe...")
    df = clean_and_tag_dataset()

    # 1. Full Climatology Dataset (2015-2025)
    logger.info("Writing full canonical dataset to %s...", CANONICAL_FULL_PATH)
    df.to_parquet(CANONICAL_FULL_PATH, index=False, engine="pyarrow", compression="snappy")
    logger.info("Saved full canonical dataset: %d rows, %d columns", len(df), len(df.columns))

    # 2. Modern Multivariate Forecasting Dataset (2021-2025)
    # P2-DEC-01: Filter strictly to 2021-01-01 onwards for multi-variable forecasting
    logger.info("Filtering for modern multivariate forecasting view (>= 2021-01-01)...")
    df_forecast = df[df["date_of_record"] >= "2021-01-01"].copy().reset_index(drop=True)
    logger.info("Writing forecasting dataset to %s...", CANONICAL_FORECAST_PATH)
    df_forecast.to_parquet(CANONICAL_FORECAST_PATH, index=False, engine="pyarrow", compression="snappy")
    logger.info("Saved forecasting canonical dataset: %d rows, %d columns", len(df_forecast), len(df_forecast.columns))

    # 3. Canonical Physical Station Registry
    logger.info("Building canonical station registry...")
    stn_registry = {}
    for stn_id, group in df.groupby("station_id"):
        stn_registry[stn_id] = {
            "station_id": stn_id,
            "station_name": group["station_name"].iloc[0],
            "state": group["state"].iloc[0],
            "district": group["district"].iloc[0],
            "latitude": float(group["latitude"].iloc[0]),
            "longitude": float(group["longitude"].iloc[0]),
            "elevation_m": int(group["elevation"].iloc[0]),
            "record_count_total": int(len(group)),
            "record_count_modern_2021_2025": int((group["date_of_record"] >= "2021-01-01").sum()),
            "first_observed_date": str(group["date_of_record"].min().date()),
            "last_observed_date": str(group["date_of_record"].max().date()),
        }

    with open(STATION_REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(stn_registry, f, indent=2)
    logger.info("Saved station registry with %d physical stations to %s", len(stn_registry), STATION_REGISTRY_PATH)

    # 4. Data Dictionary
    logger.info("Generating canonical data dictionary...")
    data_dict = {
        "dataset_name": "India Weather & Rainfall Canonical Dataset",
        "version": "2.0.0",
        "phase": "Phase 2 Canonical",
        "total_records_full": len(df),
        "total_records_forecasting_view": len(df_forecast),
        "unique_physical_stations": len(stn_registry),
        "fields": {
            "station_id": "Primary key: deterministic physical identifier {slug}_{lat:.4f}_{lon:.4f}_{elev}m",
            "date_of_record": "Timestamp of daily record (YYYY-MM-DD)",
            "month": "Month name string (January - December)",
            "season": "Climatological season (Winter, Summer, Monsoon, Post-monsoon)",
            "station_name": "Official station name string",
            "state": "Two-letter state / Union Territory administrative code",
            "district": "Administrative district name",
            "avg_temp": "Raw recorded daily average temperature (Celsius)",
            "min_temp": "Raw recorded daily minimum temperature (Celsius)",
            "max_temp": "Raw recorded daily maximum temperature (Celsius)",
            "wind_speed": "Recorded daily wind speed (km/h)",
            "air_pressure": "Recorded atmospheric sea-level/station pressure (hPa)",
            "elevation": "Elevation above sea level (meters)",
            "latitude": "Latitude in decimal degrees North",
            "longitude": "Longitude in decimal degrees East",
            "rainfall": "Daily rainfall depth (mm); 0.0=measured dry day, NaN=missing sensor reading",
            "qc_flag_temp": "Quality control flag: VALID, INVERSION_MIN_GT_MAX, EXTREME_OUTLIER, AVG_OUT_OF_BOUNDS",
            "avg_temp_clean": "ML feature view with corrupted temperature values masked as NaN",
            "min_temp_clean": "ML feature view with corrupted temperature values masked as NaN",
            "max_temp_clean": "ML feature view with corrupted temperature values masked as NaN"
        }
    }
    with open(DATA_DICTIONARY_PATH, "w", encoding="utf-8") as f:
        json.dump(data_dict, f, indent=2)
    logger.info("Saved data dictionary to %s", DATA_DICTIONARY_PATH)

    return df, df_forecast

if __name__ == "__main__":
    from typing import Tuple
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    build_canonical_artifacts()
