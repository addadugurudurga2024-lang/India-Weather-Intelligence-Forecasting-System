"""
Module for loading, verifying raw integrity, and providing cached read-only access
to the authoritative weather dataset for Phase 1 Audit.
CRITICAL: Raw source file is NEVER altered or overwritten.
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd

logger = logging.getLogger("phase1_audit.data_loader")

RAW_DATA_PATH = Path(r"D:\Downloads\india_weather_rainfall_data.xlsx")
CACHE_DIR = Path(r"D:\weather_forcasting\phase1_audit\cache")
CACHE_PARQUET_PATH = CACHE_DIR / "india_weather_rainfall_data_cached.parquet"
INTEGRITY_LOG_PATH = CACHE_DIR / "source_integrity.json"


def compute_file_hash_and_stats(path: Path) -> Dict[str, Any]:
    """Compute sha256, file size, and modification time of the raw source file."""
    if not path.exists():
        raise FileNotFoundError(f"Source file not found at: {path}")
    
    stat = path.stat()
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(4 * 1024 * 1024):
            hasher.update(chunk)
    
    return {
        "file_path": str(path),
        "size_bytes": stat.st_size,
        "mtime": stat.st_mtime,
        "sha256": hasher.hexdigest(),
    }


def verify_source_integrity(expected_reference: Dict[str, Any] = None) -> bool:
    """Verify that the raw source file has not been altered in any way."""
    current = compute_file_hash_and_stats(RAW_DATA_PATH)
    if expected_reference is None:
        if INTEGRITY_LOG_PATH.exists():
            with open(INTEGRITY_LOG_PATH, "r", encoding="utf-8") as f:
                expected_reference = json.load(f)
        else:
            return True
    
    match = (
        current["size_bytes"] == expected_reference["size_bytes"]
        and current["sha256"] == expected_reference["sha256"]
    )
    if not match:
        logger.critical(
            "SOURCE FILE INTEGRITY COMPROMISED! Current: %s vs Expected: %s",
            current, expected_reference
        )
    return match


def load_authoritative_data(force_reload: bool = False) -> pd.DataFrame:
    """
    Load the dataset. If cached parquet exists and source hash matches, load parquet for
    100x speedup across audit tasks. If not, reads raw xlsx with calamine and writes cache.
    The returned DataFrame represents the exact raw data as read from the xlsx file.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check or record source integrity
    current_meta = compute_file_hash_and_stats(RAW_DATA_PATH)
    if not INTEGRITY_LOG_PATH.exists() or force_reload:
        with open(INTEGRITY_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(current_meta, f, indent=2)
        logger.info("Recorded initial source integrity reference: %s", current_meta)
    else:
        with open(INTEGRITY_LOG_PATH, "r", encoding="utf-8") as f:
            expected = json.load(f)
        if current_meta["sha256"] != expected["sha256"]:
            raise RuntimeError(
                f"Source dataset SHA256 mismatch! Raw file was modified! "
                f"Recorded: {expected['sha256']}, Observed: {current_meta['sha256']}"
            )

    if CACHE_PARQUET_PATH.exists() and not force_reload:
        logger.info("Loading cached raw dataframe from %s...", CACHE_PARQUET_PATH)
        df = pd.read_parquet(CACHE_PARQUET_PATH)
        logger.info("Loaded cached DataFrame successfully: %s rows, %s cols", df.shape[0], df.shape[1])
        return df

    logger.info("Reading authoritative raw excel file via python-calamine engine: %s...", RAW_DATA_PATH)
    df = pd.read_excel(RAW_DATA_PATH, engine="calamine")
    logger.info("Raw dataset loaded from Excel: %s rows, %s cols. Writing cache parquet...", df.shape[0], df.shape[1])
    df.to_parquet(CACHE_PARQUET_PATH, index=False)
    logger.info("Cached parquet created at %s", CACHE_PARQUET_PATH)
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    df = load_authoritative_data()
    print("Shape:", df.shape)
    print("Columns:", list(df.columns))
    print("Integrity Verified:", verify_source_integrity())
