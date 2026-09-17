"""
Phase 2: Cleaning, Quality Flagging & Canonical Station Assignment
Implements:
- P2-DEC-02: Composite station_id assignment.
- P2-DEC-03: Resolution of Jamshedpur 140m vs 128m duplicate pairs (retaining canonical 140m tower).
- P2-DEC-05: Non-destructive quality audit flags (qc_flag_temp).
- Schema standardisation and clean numerical views.
"""

import logging
import sys
from pathlib import Path
from typing import Tuple
import numpy as np
import pandas as pd

# Add local path
sys.path.append(str(Path(__file__).parent))
sys.path.append(r"D:\weather_forcasting\phase1_audit\scripts")

from config import (
    generate_station_id,
    CANONICAL_JAMSHEDPUR_ELEVATION,
    MAX_TEMP_CEILING,
    MIN_TEMP_FLOOR
)
from data_loader import load_authoritative_data, verify_source_integrity

logger = logging.getLogger("phase2_canonical.clean")

def clean_and_tag_dataset() -> pd.DataFrame:
    """
    Reads authoritative raw weather data, applies verified Phase 2 deduplication,
    attaches physical composite station_id, and tags quality control flags without
    destructive loss of provenance.
    """
    logger.info("Verifying raw source integrity prior to cleaning...")
    if not verify_source_integrity():
        raise RuntimeError("Raw source integrity compromised!")

    logger.info("Loading raw weather data from verified cache...")
    df = load_authoritative_data()
    n_raw = len(df)
    logger.info("Raw input rows: %d", n_raw)

    # 1. P2-DEC-03: Resolve Jamshedpur 1,490 duplicate records
    # Keep the canonical elevation of 140m (the IMD standard observation mast)
    logger.info("Applying P2-DEC-03: Resolving Jamshedpur duplicate pairs...")
    jamshedpur_mask = df["station_name"] == "Jamshedpur"
    jamshedpur_non_canonical = jamshedpur_mask & (df["elevation"] != CANONICAL_JAMSHEDPUR_ELEVATION)
    n_dropped_jamshedpur = jamshedpur_non_canonical.sum()
    logger.info("Filtering %d non-canonical Jamshedpur duplicate rows (elevation 128m)...", n_dropped_jamshedpur)
    df = df[~jamshedpur_non_canonical].copy()
    logger.info("Rows after resolving Jamshedpur duplicates: %d", len(df))

    # 2. P2-DEC-02: Construct deterministic, composite physical station identifier
    logger.info("Assigning deterministic physical station_id...")
    df["station_id"] = [
        generate_station_id(stn, lat, lon, elev)
        for stn, lat, lon, elev in zip(df["station_name"], df["latitude"], df["longitude"], df["elevation"])
    ]

    # Verify that (station_id, date_of_record) is 100% UNIQUE
    dups = df.duplicated(subset=["station_id", "date_of_record"]).sum()
    logger.info("Duplicate check on (station_id, date_of_record): %d duplicates found", dups)
    if dups > 0:
        raise ValueError(f"CRITICAL: Found {dups} duplicate records on (station_id, date_of_record)!")

    # 3. P2-DEC-05: Non-destructive Quality Control (QC) Flagging
    logger.info("Calculating quality control flags for temperature...")
    # Initialize QC flag as VALID
    qc_flags = np.full(len(df), "VALID", dtype=object)

    # Extreme outlier (> 60C or < -40C)
    extreme_outlier = (df["max_temp"] > MAX_TEMP_CEILING) | (df["avg_temp"] > MAX_TEMP_CEILING) | (df["min_temp"] < MIN_TEMP_FLOOR)
    qc_flags[extreme_outlier] = "EXTREME_OUTLIER"

    # Inversion: min_temp > max_temp
    min_gt_max = (df["min_temp"] > df["max_temp"]) & df["min_temp"].notna() & df["max_temp"].notna()
    qc_flags[min_gt_max] = "INVERSION_MIN_GT_MAX"

    # avg_temp outside [min_temp, max_temp] (only where min <= max and not extreme)
    avg_out_of_bounds = (
        ((df["avg_temp"] < df["min_temp"]) | (df["avg_temp"] > df["max_temp"]))
        & df["min_temp"].notna()
        & df["max_temp"].notna()
        & ~min_gt_max
        & ~extreme_outlier
    )
    qc_flags[avg_out_of_bounds] = "AVG_OUT_OF_BOUNDS"

    df["qc_flag_temp"] = qc_flags
    logger.info("QC Flag summary:\n%s", df["qc_flag_temp"].value_counts().to_dict())

    # 4. Clean temperature view (preserves raw fields in raw columns, creates clean ML views)
    df["avg_temp_clean"] = df["avg_temp"].copy()
    df["min_temp_clean"] = df["min_temp"].copy()
    df["max_temp_clean"] = df["max_temp"].copy()

    # For ML pipelines, mask invalid/corrupt temperature readings as NaN
    invalid_mask = df["qc_flag_temp"] != "VALID"
    df.loc[invalid_mask, "avg_temp_clean"] = np.nan
    df.loc[invalid_mask, "min_temp_clean"] = np.nan
    df.loc[invalid_mask, "max_temp_clean"] = np.nan

    # 5. Type casting & Sorting
    df["date_of_record"] = pd.to_datetime(df["date_of_record"])
    df["elevation"] = df["elevation"].astype(np.int32)
    df["latitude"] = df["latitude"].astype(np.float64)
    df["longitude"] = df["longitude"].astype(np.float64)

    # Sort deterministically by physical station and chronological date
    df = df.sort_values(by=["station_id", "date_of_record"]).reset_index(drop=True)
    logger.info("Dataset cleaning complete. Final canonical row count: %d", len(df))
    return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    clean_df = clean_and_tag_dataset()
    print("Cleaned shape:", clean_df.shape)
    print("Station count:", clean_df["station_id"].nunique())
