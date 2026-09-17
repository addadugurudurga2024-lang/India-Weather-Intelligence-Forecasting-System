"""
Phase 2: Master Orchestration Pipeline
Executes data cleaning, canonical dataset building, feature engineering,
temporal splitting, and test validations end-to-end.
"""

import logging
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(r"D:\weather_forcasting\phase1_audit\scripts")

from config import LOGS_DIR
from build_canonical_dataset import build_canonical_artifacts
from feature_engineering import engineer_forecasting_features
from temporal_split_builder import build_temporal_splits
from data_loader import verify_source_integrity

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "phase2_pipeline.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("phase2_canonical.pipeline")

def run_pipeline():
    logger.info("==================================================")
    logger.info("  STARTING PHASE 2 PRODUCTION CANONICAL PIPELINE  ")
    logger.info("==================================================")

    # 1. Source verification check
    logger.info("Step 1: Checking raw immutable dataset integrity...")
    if not verify_source_integrity():
        raise RuntimeError("Source dataset SHA256 integrity check failed!")
    logger.info("Source file SHA256 confirmed unchanged.")

    # 2. Build canonical artifacts
    logger.info("Step 2: Cleaning and assembling canonical datasets...")
    df_full, df_forecast = build_canonical_artifacts()

    # 3. Feature engineering
    logger.info("Step 3: Engineering gap-aware lags, rolling features, and targets...")
    df_features = engineer_forecasting_features()

    # 4. Chronological splits
    logger.info("Step 4: Building walk-forward chronological validation manifests...")
    manifest = build_temporal_splits()

    logger.info("==================================================")
    logger.info("  PHASE 2 PIPELINE COMPLETED SUCCESSFULLY!        ")
    logger.info("  Full Dataset: %d rows                          ", len(df_full))
    logger.info("  Forecasting Dataset: %d rows                   ", len(df_forecast))
    logger.info("  Engineered Features: %d columns                ", len(df_features.columns))
    logger.info("==================================================")

if __name__ == "__main__":
    run_pipeline()
