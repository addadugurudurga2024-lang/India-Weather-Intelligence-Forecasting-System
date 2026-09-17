"""
Phase 1.5 Verification Suite - Baseline Dataset Metrics & Integrity
Recalculates records, columns, dates, data types, missing counts, and national continuity.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any
import pandas as pd
# pyrefly: ignore [missing-import]
from data_loader import RAW_DATA_PATH, compute_file_hash_and_stats, load_authoritative_data

logger = logging.getLogger("phase1_verification.baseline")

def verify_baseline() -> Dict[str, Any]:
    logger.info("Computing source raw integrity...")
    integrity = compute_file_hash_and_stats(RAW_DATA_PATH)
    
    logger.info("Loading dataset for baseline verification...")
    df = load_authoritative_data()
    
    n_rows, n_cols = df.shape
    min_date = df['date_of_record'].min()
    max_date = df['date_of_record'].max()
    unique_dates = df['date_of_record'].nunique()
    expected_calendar_days = (max_date - min_date).days + 1
    
    missing_dict = df.isna().sum().to_dict()
    dtypes_dict = {col: str(df[col].dtype) for col in df.columns}
    
    baseline_results = {
        "raw_integrity": integrity,
        "records": int(n_rows),
        "columns_count": int(n_cols),
        "columns_list": list(df.columns),
        "min_date": str(min_date),
        "max_date": str(max_date),
        "unique_dates": int(unique_dates),
        "expected_calendar_days": int(expected_calendar_days),
        "missing_calendar_days": int(expected_calendar_days - unique_dates),
        "missing_counts": {k: int(v) for k, v in missing_dict.items()},
        "dtypes": dtypes_dict,
        "unique_states": int(df['state'].nunique()),
        "unique_districts": int(df['district'].nunique()),
        "unique_station_names": int(df['station_name'].nunique()),
        "unique_station_coords": int(df[['station_name', 'latitude', 'longitude']].drop_duplicates().shape[0]),
        "unique_coords": int(df[['latitude', 'longitude']].drop_duplicates().shape[0])
    }
    return baseline_results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    res = verify_baseline()
    out_path = Path(r"D:\weather_forcasting\phase1_verification\outputs\baseline_verification.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print("Baseline verification completed. Written to:", out_path)
