import hashlib
import json
from pathlib import Path
import pandas as pd

RAW_SOURCE_PATH = Path(r"D:\Downloads\india_weather_rainfall_data.xlsx")
EXPECTED_SHA256 = "e6a636777430f078b4d970f9f46e79efcece7f97b67dd186c30a755d2783cd84"

PHASE2_DIR = Path(r"d:\weather_forcasting\phase2_canonical\outputs")
FEATURES_PARQUET = PHASE2_DIR / "features_engineered.parquet"
SPLIT_MANIFEST = PHASE2_DIR / "temporal_split_manifest.json"
STATION_METADATA = PHASE2_DIR / "station_metadata.json"
CANONICAL_FULL = PHASE2_DIR / "canonical_weather_full.parquet"
CANONICAL_FC = PHASE2_DIR / "canonical_weather_forecasting.parquet"

def verify_entry_gate():
    results = {}
    
    # 1. Source Hash
    assert RAW_SOURCE_PATH.exists(), f"Raw source {RAW_SOURCE_PATH} not found!"
    hasher = hashlib.sha256()
    with open(RAW_SOURCE_PATH, "rb") as f:
        while chunk := f.read(8192 * 1024):
            hasher.update(chunk)
    actual_hash = hasher.hexdigest()
    assert actual_hash == EXPECTED_SHA256, f"Hash mismatch: {actual_hash} != {EXPECTED_SHA256}"
    results["raw_source_hash"] = actual_hash
    results["raw_source_verified"] = True
    
    # 2. Check Phase 2 artifacts
    for name, path in [
        ("features_engineered", FEATURES_PARQUET),
        ("temporal_split_manifest", SPLIT_MANIFEST),
        ("station_metadata", STATION_METADATA),
        ("canonical_weather_full", CANONICAL_FULL),
        ("canonical_weather_forecasting", CANONICAL_FC)
    ]:
        assert path.exists(), f"Phase 2 artifact missing: {path}"
        results[f"{name}_exists"] = True

    # 3. Validate features_engineered dataset
    df = pd.read_parquet(FEATURES_PARQUET)
    results["total_rows"] = len(df)
    results["total_columns"] = len(df.columns)
    results["unique_stations"] = int(df["station_id"].nunique())
    results["date_min"] = str(df["date_of_record"].min())
    results["date_max"] = str(df["date_of_record"].max())
    
    expected_targets = [
        "target_next_day_temp",
        "target_next_day_rainfall_amount",
        "target_next_day_rain_binary"
    ]
    for target in expected_targets:
        assert target in df.columns, f"Missing target: {target}"
        valid_cnt = int(df[target].notna().sum())
        nan_cnt = int(df[target].isna().sum())
        results[f"{target}_valid_count"] = valid_cnt
        results[f"{target}_nan_count"] = nan_cnt
        
    # Check uniqueness of (station_id, date_of_record)
    dup_count = int(df.duplicated(subset=["station_id", "date_of_record"]).sum())
    assert dup_count == 0, f"Found {dup_count} duplicate station-date pairs!"
    results["duplicates"] = dup_count

    # 4. Validate split manifest
    with open(SPLIT_MANIFEST, "r") as f:
        manifest = json.load(f)
    results["manifest_strategy"] = manifest.get("validation_strategy")
    results["manifest_folds_count"] = len(manifest.get("folds", []))
    results["holdout_start"] = manifest["holdout_test_set"]["period"]["start"]
    results["holdout_end"] = manifest["holdout_test_set"]["period"]["end"]
    
    print(json.dumps(results, indent=2))
    return results

if __name__ == "__main__":
    verify_entry_gate()
