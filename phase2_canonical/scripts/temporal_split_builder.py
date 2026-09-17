"""
Phase 2: Temporal Split Builder (Expanding Window / Walk-Forward Cross-Validation)
Defines strict chronological partition manifests preventing temporal & synoptic leakage:
- Fold 1: Train 2021-2022, Val 2023
- Fold 2: Train 2021-2023, Val 2024
- Holdout Test: 2025-01-01 to 2025-02-10 (out-of-time evaluation)
"""

import json
import logging
import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).parent))

from config import FEATURE_STORE_PATH, SPLIT_MANIFEST_PATH

logger = logging.getLogger("phase2_canonical.splits")

def build_temporal_splits() -> dict:
    logger.info("Loading feature store from %s to construct split manifests...", FEATURE_STORE_PATH)
    df = pd.read_parquet(FEATURE_STORE_PATH, columns=["date_of_record"])

    min_date = df["date_of_record"].min()
    max_date = df["date_of_record"].max()
    logger.info("Dataset span: %s to %s", min_date.date(), max_date.date())

    manifest = {
        "validation_strategy": "Expanding Window Chronological Split (Walk-Forward)",
        "unit_of_time": "Calendar Day (Daily Panel)",
        "total_records": len(df),
        "dataset_start": str(min_date.date()),
        "dataset_end": str(max_date.date()),
        "folds": [
            {
                "fold_id": 1,
                "train_period": {"start": "2021-01-01", "end": "2022-12-31"},
                "val_period": {"start": "2023-01-01", "end": "2023-12-31"},
                "train_records": int(((df["date_of_record"] >= "2021-01-01") & (df["date_of_record"] <= "2022-12-31")).sum()),
                "val_records": int(((df["date_of_record"] >= "2023-01-01") & (df["date_of_record"] <= "2023-12-31")).sum())
            },
            {
                "fold_id": 2,
                "train_period": {"start": "2021-01-01", "end": "2023-12-31"},
                "val_period": {"start": "2024-01-01", "end": "2024-12-31"},
                "train_records": int(((df["date_of_record"] >= "2021-01-01") & (df["date_of_record"] <= "2023-12-31")).sum()),
                "val_records": int(((df["date_of_record"] >= "2024-01-01") & (df["date_of_record"] <= "2024-12-31")).sum())
            }
        ],
        "holdout_test_set": {
            "period": {"start": "2025-01-01", "end": str(max_date.date())},
            "records": int((df["date_of_record"] >= "2025-01-01").sum()),
            "description": "Strict out-of-time unobserved holdout test partition."
        }
    }

    with open(SPLIT_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info("Saved temporal split manifest to %s", SPLIT_MANIFEST_PATH)

    return manifest

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    splits = build_temporal_splits()
    print("Folds created:")
    for fold in splits["folds"]:
        print(f"Fold {fold['fold_id']}: Train {fold['train_records']} rows | Val {fold['val_records']} rows")
    print(f"Holdout: {splits['holdout_test_set']['records']} rows")
