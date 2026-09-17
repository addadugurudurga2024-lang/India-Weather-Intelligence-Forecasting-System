import sys
from pathlib import Path
import pandas as pd
import torch

sys.path.append(str(Path(__file__).parent.parent / "scripts"))

# pyrefly: ignore [missing-import]
from data_loaders import prepare_xgboost_data, get_holdout_data, get_lstm_dataloaders
# pyrefly: ignore [missing-import]
import model_config as cfg

def test_data_leakage():
    """Verify that train, validation, and holdout dates do not overlap."""
    X_train, y_train, X_val, y_val = prepare_xgboost_data(fold_id=1, target=cfg.TARGET_TEMP)
    X_test, y_test = get_holdout_data(target=cfg.TARGET_TEMP)
    
    # Reconstruct data to get dates. Wait, prepare_xgboost_data returns only FEATURE_COLS.
    # So we need to load the dataframe directly and check dates.
    df = pd.read_parquet(cfg.DATA_PATH)
    
    train_dates = df[(df["date_of_record"] >= "2021-01-01") & (df["date_of_record"] <= "2022-12-31")]["date_of_record"].unique()
    val_dates = df[(df["date_of_record"] >= "2023-01-01") & (df["date_of_record"] <= "2023-12-31")]["date_of_record"].unique()
    test_dates = df[(df["date_of_record"] >= "2025-01-01") & (df["date_of_record"] <= "2025-02-10")]["date_of_record"].unique()
    
    # Check intersections
    assert len(set(train_dates).intersection(set(val_dates))) == 0, "Leakage: Train and Validation dates overlap in Fold 1"
    assert len(set(train_dates).intersection(set(test_dates))) == 0, "Leakage: Train and Test dates overlap"
    assert len(set(val_dates).intersection(set(test_dates))) == 0, "Leakage: Validation and Test dates overlap"

def test_lstm_shapes():
    """Verify that LSTM dataloaders return the correct shapes."""
    train_loader, val_loader = get_lstm_dataloaders(fold_id=1, target=cfg.TARGET_TEMP)
    
    X_batch, y_batch = next(iter(train_loader))
    
    assert len(X_batch.shape) == 3, f"Expected 3D input tensor, got {X_batch.shape}"
    assert X_batch.shape[1] == cfg.LSTM_CONFIG["sequence_length"], f"Expected sequence length {cfg.LSTM_CONFIG['sequence_length']}, got {X_batch.shape[1]}"
    assert X_batch.shape[2] == len(cfg.FEATURE_COLS), f"Expected {len(cfg.FEATURE_COLS)} features, got {X_batch.shape[2]}"
    assert len(y_batch.shape) == 1, f"Expected 1D target tensor, got {y_batch.shape}"

def test_target_presence():
    """Verify targets exist and are accessible."""
    df = pd.read_parquet(cfg.DATA_PATH)
    assert cfg.TARGET_TEMP in df.columns, f"Target {cfg.TARGET_TEMP} not found in canonical data"
    assert cfg.TARGET_RAIN_BIN in df.columns, f"Target {cfg.TARGET_RAIN_BIN} not found in canonical data"

if __name__ == "__main__":
    print("Running test_data_leakage...")
    test_data_leakage()
    print("Running test_lstm_shapes...")
    test_lstm_shapes()
    print("Running test_target_presence...")
    test_target_presence()
    print("All tests passed!")
