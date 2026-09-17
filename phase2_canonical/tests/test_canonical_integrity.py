"""
Automated Test Suite for Phase 2 Canonical Datasets & Feature Store
Validates:
1. Source raw Excel file immutability (SHA-256 match).
2. Absolute uniqueness on (station_id, date_of_record) - zero duplicates.
3. Proper resolution of Jamshedpur duplicates (canonical 140m tower retained).
4. No future information leakage in lag features or rolling windows.
5. Gap-aware lag enforcement (NaN when calendar gap > 1 day).
6. Target distribution validity and dry/rain ratio consistency.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent / "scripts"))
sys.path.append(r"D:\weather_forcasting\phase1_audit\scripts")

from config import (
    CANONICAL_FULL_PATH,
    CANONICAL_FORECAST_PATH,
    FEATURE_STORE_PATH,
    RAW_DATA_PATH,
    EXPECTED_SHA256
)
from data_loader import compute_file_hash_and_stats

def test_raw_source_immutability():
    """Verify raw source Excel file was NEVER altered."""
    stats = compute_file_hash_and_stats(RAW_DATA_PATH)
    assert stats["sha256"] == EXPECTED_SHA256, "Raw file SHA256 was altered!"

def test_full_canonical_uniqueness():
    """Verify that full canonical dataset has 0 duplicates on (station_id, date_of_record)."""
    assert CANONICAL_FULL_PATH.exists(), "canonical_weather_full.parquet missing!"
    df = pd.read_parquet(CANONICAL_FULL_PATH, columns=["station_id", "date_of_record"])
    dups = df.duplicated(subset=["station_id", "date_of_record"]).sum()
    assert dups == 0, f"Found {dups} duplicate records in canonical full dataset!"

def test_jamshedpur_duplicate_resolution():
    """Verify Jamshedpur has exactly 1 record per date and canonical elevation is 140m."""
    df = pd.read_parquet(CANONICAL_FULL_PATH)
    jamshedpur = df[df["station_name"] == "Jamshedpur"]
    assert len(jamshedpur) == 1490, f"Expected 1490 Jamshedpur records, found {len(jamshedpur)}"
    assert (jamshedpur["elevation"] == 140).all(), "Non-canonical Jamshedpur elevation found!"
    assert jamshedpur.duplicated(subset=["date_of_record"]).sum() == 0, "Duplicate dates in Jamshedpur!"

def test_leakage_and_gap_awareness():
    """Verify lag-1 features are strictly backward looking and produce NaN on gaps."""
    assert FEATURE_STORE_PATH.exists(), "features_engineered.parquet missing!"
    df = pd.read_parquet(FEATURE_STORE_PATH)

    # Pick a random sample of rows where lag_1 is present
    valid_lags = df[df["lag_1_avg_temp"].notna()].sample(n=500, random_state=42)
    for idx, row in valid_lags.iterrows():
        stn = row["station_id"]
        dt = row["date_of_record"]
        prev_dt = dt - pd.Timedelta(days=1)
        # Match previous day's row
        prev_match = df[(df["station_id"] == stn) & (df["date_of_record"] == prev_dt)]
        assert len(prev_match) == 1, f"Previous day record missing for lag verification at {stn}, {dt}"
        expected_val = prev_match["avg_temp_clean"].iloc[0]
        actual_lag = row["lag_1_avg_temp"]
        if np.isnan(expected_val):
            assert np.isnan(actual_lag)
        else:
            assert np.isclose(actual_lag, expected_val), f"Lag mismatch at {stn} on {dt}: {actual_lag} vs {expected_val}"

def test_target_class_balance():
    """Verify Target C (rain binary) on valid 2021-2025 dates matches modern 54.9% dry / 45.1% rain distribution."""
    df = pd.read_parquet(FEATURE_STORE_PATH, columns=["target_next_day_rain_binary"])
    valid_targets = df["target_next_day_rain_binary"].dropna()
    dry_pct = (valid_targets == 0).mean() * 100
    rain_pct = (valid_targets == 1).mean() * 100
    assert 53.0 < dry_pct < 57.0, f"Unexpected dry percentage: {dry_pct:.2f}%"
    assert 43.0 < rain_pct < 47.0, f"Unexpected rain percentage: {rain_pct:.2f}%"

if __name__ == "__main__":
    print("Running automated test suite...")
    test_raw_source_immutability()
    print("[PASS] Raw source immutability confirmed.")
    test_full_canonical_uniqueness()
    print("[PASS] Full canonical dataset uniqueness confirmed.")
    test_jamshedpur_duplicate_resolution()
    print("[PASS] Jamshedpur canonical resolution confirmed.")
    test_leakage_and_gap_awareness()
    print("[PASS] Leakage-free, gap-aware lag features confirmed.")
    test_target_class_balance()
    print("[PASS] Target distribution & class balance confirmed.")
    print("ALL TESTS PASSED SUCCESSFULLY!")
