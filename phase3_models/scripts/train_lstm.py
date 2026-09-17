import os
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix
)
import joblib

from lstm_dataset import create_station_sequences

BASE_DIR = Path(r"d:\weather_forcasting\phase3_models")
LSTM_DIR = BASE_DIR / "lstm"
PREPROC_DIR = BASE_DIR / "preprocessors"
PRED_DIR = BASE_DIR / "predictions"
METRICS_DIR = BASE_DIR / "metrics"
PLOTS_DIR = BASE_DIR / "plots"

FEATURES_PARQUET = Path(r"d:\weather_forcasting\phase2_canonical\outputs\features_engineered.parquet")

FEATURES = [
    "avg_temp_clean", "min_temp_clean", "max_temp_clean",
    "wind_speed", "air_pressure", "rainfall",
    "elevation", "latitude", "longitude",
    "doy_sin", "doy_cos", "month_sin", "month_cos",
    "lag_1_avg_temp", "lag_2_avg_temp", "lag_1_min_temp", "lag_1_max_temp",
    "lag_1_rainfall", "lag_2_rainfall", "lag_1_wind_speed", "lag_1_air_pressure",
    "rolling_3d_temp_mean", "rolling_7d_temp_mean", "rolling_7d_temp_std",
    "rolling_3d_rainfall_sum", "rolling_7d_rainfall_sum"
]

FOLDS = {
    "fold1": {
        "train": ("2021-01-01", "2022-12-31"),
        "val": ("2023-01-01", "2023-12-31")
    },
    "fold2": {
        "train": ("2021-01-01", "2023-12-31"),
        "val": ("2024-01-01", "2024-12-31")
    }
}
HOLDOUT_PERIOD = ("2025-01-01", "2025-02-10")
SEQ_LEN = 7

class WeatherLSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim=48, num_layers=2, dropout=0.2, task_type="regression"):
        super().__init__()
        self.task_type = task_type
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.head = nn.Sequential(
            nn.Linear(hidden_dim, 24),
            nn.ReLU(),
            nn.Linear(24, 1)
        )

    def forward(self, x):
        # x: (batch, seq_len, input_dim)
        out, (hn, cn) = self.lstm(x)
        # Use representation at last sequence timestep
        last_step = out[:, -1, :]
        logits = self.head(last_step).squeeze(-1)
        return logits

def train_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0.0
    total_count = 0
    for X_b, y_b in loader:
        X_b, y_b = X_b.to(device), y_b.to(device)
        optimizer.zero_grad()
        preds = model(X_b)
        loss = criterion(preds, y_b)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        total_loss += loss.item() * len(y_b)
        total_count += len(y_b)
    return total_loss / total_count

def eval_epoch(model, loader, criterion, device):
    model.eval()
    total_loss = 0.0
    total_count = 0
    all_preds = []
    all_targets = []
    with torch.no_grad():
        for X_b, y_b in loader:
            X_b, y_b = X_b.to(device), y_b.to(device)
            preds = model(X_b)
            loss = criterion(preds, y_b)
            total_loss += loss.item() * len(y_b)
            total_count += len(y_b)
            all_preds.append(preds.cpu().numpy())
            all_targets.append(y_b.cpu().numpy())
    val_loss = total_loss / total_count
    return val_loss, np.concatenate(all_preds), np.concatenate(all_targets)

def train_lstm_target(df, target_col, task_type="regression", transform_log=False):
    target_name = "temperature" if "temp" in target_col else ("rainfall" if "amount" in target_col else "rain_classification")
    print(f"\n=======================================================")
    print(f"Training LSTM for {target_name.upper()} ({task_type})")
    print(f"=======================================================")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using compute device: {device}")
    
    results = {}
    best_model_state = None
    best_scaler = None
    
    # Subsample data slightly for clean sequences if necessary or use full
    work_df = df.copy()
    if transform_log:
        work_df[target_col] = np.log1p(work_df[target_col].clip(lower=0))

    for fold_name, dates in FOLDS.items():
        print(f"\n--- {fold_name.upper()} Preparation ---")
        train_df = work_df[(work_df["date_of_record"] >= dates["train"][0]) & (work_df["date_of_record"] <= dates["train"][1])].copy()
        val_df = work_df[(work_df["date_of_record"] >= dates["val"][0]) & (work_df["date_of_record"] <= dates["val"][1])].copy()

        train_ds, train_meta, scaler = create_station_sequences(
            train_df, FEATURES, target_col, seq_len=SEQ_LEN, scaler=None, is_train=True
        )
        val_ds, val_meta, _ = create_station_sequences(
            val_df, FEATURES, target_col, seq_len=SEQ_LEN, scaler=scaler, is_train=False
        )
        
        # Save scaler for reproducibility
        joblib.dump(scaler, PREPROC_DIR / f"scaler_lstm_{target_name}_{fold_name}.joblib")

        train_loader = DataLoader(train_ds, batch_size=2048, shuffle=True, drop_last=True)
        val_loader = DataLoader(val_ds, batch_size=4096, shuffle=False)

        print(f"Dataset generated: Train sequences = {len(train_ds)}, Val sequences = {len(val_ds)}")

        model = WeatherLSTM(input_dim=len(FEATURES), hidden_dim=48, num_layers=2, dropout=0.2, task_type=task_type).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.003, weight_decay=1e-5)
        
        if task_type == "regression":
            criterion = nn.MSELoss()
        else:
            criterion = nn.BCEWithLogitsLoss()

        patience = 4
        patience_counter = 0
        best_val_loss = float("inf")
        best_fold_state = None

        t0 = time.time()
        for epoch in range(1, 13):
            train_loss = train_epoch(model, train_loader, optimizer, criterion, device)
            val_loss, val_preds_raw, val_targets_raw = eval_epoch(model, val_loader, criterion, device)
            print(f"Epoch {epoch:02d} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_fold_state = {k: v.cpu() for k, v in model.state_dict().items()}
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"Early stopping triggered at epoch {epoch}")
                    break

        train_time = round(time.time() - t0, 2)
        model.load_state_dict(best_fold_state)
        torch.save(best_fold_state, LSTM_DIR / target_name / f"lstm_{target_name}_{fold_name}.pt")
        
        # Evaluate validation set
        _, val_preds_raw, val_targets_raw = eval_epoch(model, val_loader, criterion, device)
        
        if task_type == "regression":
            if transform_log:
                y_val_actual = np.expm1(val_targets_raw)
                val_preds = np.expm1(np.clip(val_preds_raw, 0, None))
                # Rainy only
                rainy_m = y_val_actual > 0
                mae_rainy = float(mean_absolute_error(y_val_actual[rainy_m], val_preds[rainy_m]))
                rmse_rainy = float(np.sqrt(mean_squared_error(y_val_actual[rainy_m], val_preds[rainy_m])))
            else:
                y_val_actual = val_targets_raw
                val_preds = val_preds_raw
                mae_rainy = None
                rmse_rainy = None
                
            mae = float(mean_absolute_error(y_val_actual, val_preds))
            rmse = float(np.sqrt(mean_squared_error(y_val_actual, val_preds)))
            r2 = float(r2_score(y_val_actual, val_preds))
            
            results[fold_name] = {
                "mae": mae, "rmse": rmse, "r2": r2,
                "mae_rainy_only": mae_rainy, "rmse_rainy_only": rmse_rainy,
                "train_sequences": len(train_ds), "val_sequences": len(val_ds),
                "train_time_sec": train_time
            }
            print(f"{fold_name.upper()} Metrics: MAE={mae:.4f}, RMSE={rmse:.4f}, R2={r2:.4f}")

            # Save predictions
            meta_df = pd.DataFrame(val_meta, columns=["station_id", "date_of_record"])
            meta_df["actual"] = y_val_actual
            meta_df["predicted"] = val_preds
            meta_df["split"] = f"{fold_name}_val"
            meta_df["model"] = "lstm"
            meta_df["target"] = target_col
            meta_df.to_parquet(PRED_DIR / f"lstm_{target_name}_preds_{fold_name}.parquet", index=False)
            
        else: # Classification
            probs = 1.0 / (1.0 + np.exp(-val_preds_raw))
            preds_bin = (probs >= 0.5).astype(int)
            targets_bin = val_targets_raw.astype(int)
            
            results[fold_name] = {
                "accuracy": float(accuracy_score(targets_bin, preds_bin)),
                "precision": float(precision_score(targets_bin, preds_bin, zero_division=0)),
                "recall": float(recall_score(targets_bin, preds_bin, zero_division=0)),
                "f1": float(f1_score(targets_bin, preds_bin, zero_division=0)),
                "roc_auc": float(roc_auc_score(targets_bin, probs)),
                "pr_auc": float(average_precision_score(targets_bin, probs)),
                "confusion_matrix": confusion_matrix(targets_bin, preds_bin).tolist(),
                "train_sequences": len(train_ds), "val_sequences": len(val_ds),
                "train_time_sec": train_time
            }
            print(f"{fold_name.upper()} Metrics: Acc={results[fold_name]['accuracy']:.4f}, F1={results[fold_name]['f1']:.4f}, ROC-AUC={results[fold_name]['roc_auc']:.4f}")

            meta_df = pd.DataFrame(val_meta, columns=["station_id", "date_of_record"])
            meta_df["actual"] = targets_bin
            meta_df["predicted"] = preds_bin
            meta_df["probability"] = probs
            meta_df["threshold"] = 0.5
            meta_df["split"] = f"{fold_name}_val"
            meta_df["model"] = "lstm"
            meta_df["target"] = target_col
            meta_df.to_parquet(PRED_DIR / f"lstm_{target_name}_preds_{fold_name}.parquet", index=False)

        best_model_state = best_fold_state
        best_scaler = scaler

    # Holdout Evaluation using Fold 2 weights & scaler
    print(f"\n--- HOLDOUT Evaluation for {target_name.upper()} ---")
    holdout_df = work_df[(work_df["date_of_record"] >= HOLDOUT_PERIOD[0]) & (work_df["date_of_record"] <= HOLDOUT_PERIOD[1])].copy()
    hold_ds, hold_meta, _ = create_station_sequences(
        holdout_df, FEATURES, target_col, seq_len=SEQ_LEN, scaler=best_scaler, is_train=False
    )
    hold_loader = DataLoader(hold_ds, batch_size=4096, shuffle=False)
    
    eval_model = WeatherLSTM(input_dim=len(FEATURES), hidden_dim=48, num_layers=2, dropout=0.2, task_type=task_type).to(device)
    eval_model.load_state_dict(best_model_state)
    
    _, hold_preds_raw, hold_targets_raw = eval_epoch(eval_model, hold_loader, criterion, device)

    if task_type == "regression":
        if transform_log:
            y_hold_actual = np.expm1(hold_targets_raw)
            hold_preds = np.expm1(np.clip(hold_preds_raw, 0, None))
            rainy_h = y_hold_actual > 0
            mae_rainy_h = float(mean_absolute_error(y_hold_actual[rainy_h], hold_preds[rainy_h]))
            rmse_rainy_h = float(np.sqrt(mean_squared_error(y_hold_actual[rainy_h], hold_preds[rainy_h])))
        else:
            y_hold_actual = hold_targets_raw
            hold_preds = hold_preds_raw
            mae_rainy_h = None
            rmse_rainy_h = None

        results["holdout"] = {
            "mae": float(mean_absolute_error(y_hold_actual, hold_preds)),
            "rmse": float(np.sqrt(mean_squared_error(y_hold_actual, hold_preds))),
            "r2": float(r2_score(y_hold_actual, hold_preds)),
            "mae_rainy_only": mae_rainy_h, "rmse_rainy_only": rmse_rainy_h,
            "holdout_sequences": len(hold_ds)
        }
        print(f"HOLDOUT Metrics: MAE={results['holdout']['mae']:.4f}, RMSE={results['holdout']['rmse']:.4f}, R2={results['holdout']['r2']:.4f}")

        meta_df = pd.DataFrame(hold_meta, columns=["station_id", "date_of_record"])
        meta_df["actual"] = y_hold_actual
        meta_df["predicted"] = hold_preds
        meta_df["split"] = "holdout_2025"
        meta_df["model"] = "lstm"
        meta_df["target"] = target_col
        meta_df.to_parquet(PRED_DIR / f"lstm_{target_name}_preds_holdout.parquet", index=False)

    else:
        probs = 1.0 / (1.0 + np.exp(-hold_preds_raw))
        preds_bin = (probs >= 0.5).astype(int)
        targets_bin = hold_targets_raw.astype(int)
        
        results["holdout"] = {
            "accuracy": float(accuracy_score(targets_bin, preds_bin)),
            "precision": float(precision_score(targets_bin, preds_bin, zero_division=0)),
            "recall": float(recall_score(targets_bin, preds_bin, zero_division=0)),
            "f1": float(f1_score(targets_bin, preds_bin, zero_division=0)),
            "roc_auc": float(roc_auc_score(targets_bin, probs)),
            "pr_auc": float(average_precision_score(targets_bin, probs)),
            "confusion_matrix": confusion_matrix(targets_bin, preds_bin).tolist(),
            "holdout_sequences": len(hold_ds)
        }
        print(f"HOLDOUT Metrics: Acc={results['holdout']['accuracy']:.4f}, F1={results['holdout']['f1']:.4f}, ROC-AUC={results['holdout']['roc_auc']:.4f}")

        meta_df = pd.DataFrame(hold_meta, columns=["station_id", "date_of_record"])
        meta_df["actual"] = targets_bin
        meta_df["predicted"] = preds_bin
        meta_df["probability"] = probs
        meta_df["threshold"] = 0.5
        meta_df["split"] = "holdout_2025"
        meta_df["model"] = "lstm"
        meta_df["target"] = target_col
        meta_df.to_parquet(PRED_DIR / f"lstm_{target_name}_preds_holdout.parquet", index=False)

    return results

def main():
    print("Loading data for LSTM...")
    df = pd.read_parquet(FEATURES_PARQUET)
    df["date_of_record"] = pd.to_datetime(df["date_of_record"])
    
    lstm_results = {}
    lstm_results["target_a_temperature"] = train_lstm_target(df, "target_next_day_temp", task_type="regression", transform_log=False)
    lstm_results["target_b_rainfall_amount"] = train_lstm_target(df, "target_next_day_rainfall_amount", task_type="regression", transform_log=True)
    lstm_results["target_c_rain_binary"] = train_lstm_target(df, "target_next_day_rain_binary", task_type="classification", transform_log=False)
    
    with open(METRICS_DIR / "lstm_metrics.json", "w") as f:
        json.dump(lstm_results, f, indent=2)
    print("\nAll LSTM models trained and metrics saved successfully!")

if __name__ == "__main__":
    main()
