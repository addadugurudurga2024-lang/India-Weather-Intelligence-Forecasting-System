import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path

class StationIsolatedSequenceDataset(Dataset):
    """
    Station-isolated, gap-aware sequence dataset for PyTorch LSTM.
    Enforces:
    1. Zero cross-station sequences (windows never cross station boundaries).
    2. Strict temporal continuity (all steps within a sequence window must have consecutive date diff == 1 day).
    3. Target is aligned to t+1.
    """
    def __init__(self, X_sequences, y_targets, meta_indices):
        self.X = torch.tensor(X_sequences, dtype=torch.float32)
        self.y = torch.tensor(y_targets, dtype=torch.float32)
        self.meta = meta_indices # (station_id, date_of_record)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

def create_station_sequences(df, feature_cols, target_col, seq_len=7, scaler=None, is_train=False):
    """
    Constructs sequence windows strictly per station.
    Fits scaler ONLY if is_train=True.
    """
    df = df.sort_values(["station_id", "date_of_record"]).reset_index(drop=True)
    
    # 1. Scaling: Fit ONLY on training data
    features_data = df[feature_cols].copy()
    # Continuous features filled with median of training set to prevent NaN loss
    if is_train:
        scaler = StandardScaler()
        # compute medians on train
        medians = features_data.median()
        features_data = features_data.fillna(medians)
        scaled_features = scaler.fit_transform(features_data)
    else:
        assert scaler is not None, "Scaler must be provided for validation / holdout!"
        # use scaler mean as fillna
        features_data = features_data.fillna(pd.Series(scaler.mean_, index=feature_cols))
        scaled_features = scaler.transform(features_data)

    df_scaled = df[["station_id", "date_of_record", target_col]].copy()
    for i, col in enumerate(feature_cols):
        df_scaled[col] = scaled_features[:, i]

    sequences = []
    targets = []
    meta = []

    # Group by station to guarantee ZERO cross-station contamination
    for station_id, group in df_scaled.groupby("station_id"):
        if len(group) <= seq_len:
            continue
        
        group = group.reset_index(drop=True)
        dates = group["date_of_record"].values
        X_mat = group[feature_cols].values
        y_vec = group[target_col].values

        # Check consecutive calendar days
        # For a window from i to i + seq_len:
        # Step t is at index i + seq_len - 1. Target is y_vec[i + seq_len - 1].
        date_series = pd.to_datetime(group["date_of_record"])
        date_diffs = (date_series - date_series.shift(1)).dt.days.values

        for i in range(len(group) - seq_len + 1):
            target_val = y_vec[i + seq_len - 1]
            if np.isnan(target_val):
                continue
            
            # Check gap within the sequence window: all consecutive pairs in window must be exactly 1 day
            # diffs at index i+1 to i+seq_len-1 must all be 1
            if seq_len > 1:
                window_diffs = date_diffs[i + 1 : i + seq_len]
                if not (window_diffs == 1).all():
                    continue # Skip window spanning calendar gap

            seq_x = X_mat[i : i + seq_len]
            sequences.append(seq_x)
            targets.append(target_val)
            meta.append((station_id, dates[i + seq_len - 1]))

    if len(sequences) == 0:
        return None, None, scaler

    X_arr = np.array(sequences, dtype=np.float32)
    y_arr = np.array(targets, dtype=np.float32)
    dataset = StationIsolatedSequenceDataset(X_arr, y_arr, meta)
    return dataset, meta, scaler
