import json
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from pathlib import Path

import model_config as cfg

def load_data():
    """Loads the canonical dataset and split manifest."""
    df = pd.read_parquet(cfg.DATA_PATH)
    with open(cfg.SPLIT_MANIFEST_PATH, "r") as f:
        manifest = json.load(f)
    return df, manifest

def prepare_xgboost_data(fold_id=1, target=cfg.TARGET_TEMP):
    """
    Prepares training and validation datasets for a specific fold for XGBoost.
    Drops NaN targets.
    """
    df, manifest = load_data()
    
    # Find the requested fold
    fold_info = next((f for f in manifest["folds"] if f["fold_id"] == fold_id), None)
    if fold_info is None:
        raise ValueError(f"Fold {fold_id} not found in manifest.")
        
    train_start, train_end = fold_info["train_period"]["start"], fold_info["train_period"]["end"]
    val_start, val_end = fold_info["val_period"]["start"], fold_info["val_period"]["end"]
    
    # Filter by date ranges
    train_df = df[(df["date_of_record"] >= train_start) & (df["date_of_record"] <= train_end)].copy()
    val_df = df[(df["date_of_record"] >= val_start) & (df["date_of_record"] <= val_end)].copy()
    
    # Drop rows where target is NaN
    train_df = train_df.dropna(subset=[target])
    val_df = val_df.dropna(subset=[target])
    
    X_train = train_df[cfg.FEATURE_COLS]
    y_train = train_df[target]
    
    X_val = val_df[cfg.FEATURE_COLS]
    y_val = val_df[target]
    
    return X_train, y_train, X_val, y_val

def get_holdout_data(target=cfg.TARGET_TEMP):
    """Prepares the holdout dataset for testing."""
    df, manifest = load_data()
    holdout_start = manifest["holdout_test_set"]["period"]["start"]
    holdout_end = manifest["holdout_test_set"]["period"]["end"]
    
    test_df = df[(df["date_of_record"] >= holdout_start) & (df["date_of_record"] <= holdout_end)].copy()
    test_df = test_df.dropna(subset=[target])
    
    X_test = test_df[cfg.FEATURE_COLS]
    y_test = test_df[target]
    
    return X_test, y_test

class TimeSeriesDataset(Dataset):
    """
    PyTorch Dataset for multi-variate time-series forecasting.
    Creates sequence windows of length `sequence_length`.
    """
    def __init__(self, data_df, features, target, sequence_length=7):
        self.sequence_length = sequence_length
        self.target_name = target
        
        # We need to process station by station to avoid cross-station contamination in sequences
        self.samples = []
        
        # Sort by date
        data_df = data_df.sort_values(by=["station_id", "date_of_record"])
        
        # Create sequences per station
        for station_id, group in data_df.groupby("station_id"):
            # Ensure the group is sorted by date
            group = group.sort_values(by="date_of_record").reset_index(drop=True)
            
            # Convert to numpy arrays for speed
            X_arr = group[features].values
            y_arr = group[target].values
            
            # Need at least sequence_length records to form one sequence
            if len(group) < sequence_length:
                continue
                
            # Create sliding windows
            for i in range(len(group) - sequence_length):
                X_seq = X_arr[i : i + sequence_length]
                y_val = y_arr[i + sequence_length - 1] # Target is aligned with the last element of the sequence
                
                # Only add if the target is not NaN and there are no NaNs in the sequence
                if not np.isnan(y_val) and not np.isnan(X_seq).any():
                    self.samples.append((X_seq, y_val))
                    
    def __len__(self):
        return len(self.samples)
        
    def __getitem__(self, idx):
        X, y = self.samples[idx]
        return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)

def get_lstm_dataloaders(fold_id=1, target=cfg.TARGET_TEMP):
    """Returns PyTorch DataLoaders for Train and Val sets for a given fold."""
    df, manifest = load_data()
    
    fold_info = next((f for f in manifest["folds"] if f["fold_id"] == fold_id), None)
    
    train_start, train_end = fold_info["train_period"]["start"], fold_info["train_period"]["end"]
    val_start, val_end = fold_info["val_period"]["start"], fold_info["val_period"]["end"]
    
    train_df = df[(df["date_of_record"] >= train_start) & (df["date_of_record"] <= train_end)]
    val_df = df[(df["date_of_record"] >= val_start) & (df["date_of_record"] <= val_end)]
    
    # We must handle imputation/scaling since neural networks are sensitive to NaNs and scale.
    # For now, we will fill NaNs in features with 0 or mean (or rely on TimeSeriesDataset skipping them).
    # Since Phase 2 generated many NaNs for lag gaps, the dataset will skip sequences with NaNs.
    # To retain more data, we could impute. Let's do simple imputation for continuous features.
    
    # Let's fill NaNs in train and val with 0 for simplicity, to match typical padded zero states.
    train_df = train_df.copy()
    val_df = val_df.copy()
    train_df[cfg.FEATURE_COLS] = train_df[cfg.FEATURE_COLS].fillna(0)
    val_df[cfg.FEATURE_COLS] = val_df[cfg.FEATURE_COLS].fillna(0)
    
    train_dataset = TimeSeriesDataset(train_df, cfg.FEATURE_COLS, target, cfg.LSTM_CONFIG["sequence_length"])
    val_dataset = TimeSeriesDataset(val_df, cfg.FEATURE_COLS, target, cfg.LSTM_CONFIG["sequence_length"])
    
    train_loader = DataLoader(train_dataset, batch_size=cfg.LSTM_CONFIG["batch_size"], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=cfg.LSTM_CONFIG["batch_size"], shuffle=False)
    
    return train_loader, val_loader
