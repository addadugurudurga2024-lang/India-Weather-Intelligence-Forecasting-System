"""
Phase 2 Configuration and Metadata Standards
Defines paths, thresholds, slugification rules, and physical constants.
"""

from pathlib import Path
import re

# Base Paths
WORKSPACE_ROOT = Path(r"D:\weather_forcasting")
RAW_DATA_PATH = Path(r"D:\Downloads\india_weather_rainfall_data.xlsx")
EXPECTED_SHA256 = "e6a636777430f078b4d970f9f46e79efcece7f97b67dd186c30a755d2783cd84"

# Phase 2 Directories
PHASE2_DIR = WORKSPACE_ROOT / "phase2_canonical"
SCRIPTS_DIR = PHASE2_DIR / "scripts"
OUTPUTS_DIR = PHASE2_DIR / "outputs"
REPORTS_DIR = PHASE2_DIR / "reports"
TESTS_DIR = PHASE2_DIR / "tests"
LOGS_DIR = PHASE2_DIR / "logs"

# Output Artefacts
CANONICAL_FULL_PATH = OUTPUTS_DIR / "canonical_weather_full.parquet"
CANONICAL_FORECAST_PATH = OUTPUTS_DIR / "canonical_weather_forecasting.parquet"
FEATURE_STORE_PATH = OUTPUTS_DIR / "features_engineered.parquet"
STATION_REGISTRY_PATH = OUTPUTS_DIR / "station_metadata.json"
DATA_DICTIONARY_PATH = OUTPUTS_DIR / "data_dictionary.json"
SPLIT_MANIFEST_PATH = OUTPUTS_DIR / "temporal_split_manifest.json"

# Quality Thresholds & Rules
MAX_TEMP_CEILING = 60.0  # Max realistic temperature in C
MIN_TEMP_FLOOR = -40.0   # Min realistic temperature in C

# Canonical Station Elevation Selection for Jamshedpur (P2-DEC-03)
CANONICAL_JAMSHEDPUR_ELEVATION = 140

def slugify(text: str) -> str:
    """Deterministic, clean slugification of station or region names."""
    text = text.strip().lower()
    text = re.sub(r"[\s/\\-]+", "_", text)
    text = re.sub(r"[^\w_]", "", text)
    return text.strip("_")

def generate_station_id(station_name: str, lat: float, lon: float, elev: int) -> str:
    """
    Constructs a deterministic, collision-free physical station identifier:
    Format: {slug}_{latitude:.4f}_{longitude:.4f}_{elevation}m
    """
    slug = slugify(station_name)
    return f"{slug}_{lat:.4f}_{lon:.4f}_{int(elev)}m"
