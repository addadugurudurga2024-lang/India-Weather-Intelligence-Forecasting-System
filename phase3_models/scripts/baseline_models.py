import json
from pathlib import Path
import numpy as np
import pandas as pd
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

FEATURES_PARQUET = Path(r"d:\weather_forcasting\phase2_canonical\outputs\features_engineered.parquet")
SPLIT_MANIFEST = Path(r"d:\weather_forcasting\phase2_canonical\outputs\temporal_split_manifest.json")
OUTPUT_DIR = Path(r"d:\weather_forcasting\phase3_models\metrics")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def compute_regression_metrics(y_true, y_pred):
    mask = ~(np.isnan(y_true) | np.isnan(y_pred))
    y_t = y_true[mask]
    y_p = y_pred[mask]
    if len(y_t) == 0:
        return {"mae": None, "rmse": None, "r2": None, "count": 0}
    mae = float(mean_absolute_error(y_t, y_p))
    rmse = float(np.sqrt(mean_squared_error(y_t, y_p)))
    r2 = float(r2_score(y_t, y_p))
    return {"mae": mae, "rmse": rmse, "r2": r2, "count": int(len(y_t))}

def compute_classification_metrics(y_true, y_pred, y_prob=None):
    mask = ~(np.isnan(y_true) | np.isnan(y_pred))
    y_t = y_true[mask].astype(int)
    y_p = y_pred[mask].astype(int)
    if len(y_t) == 0:
        return {"accuracy": None, "precision": None, "recall": None, "f1": None, "roc_auc": None, "pr_auc": None, "count": 0}
    acc = float(accuracy_score(y_t, y_p))
    prec = float(precision_score(y_t, y_p, zero_division=0))
    rec = float(recall_score(y_t, y_p, zero_division=0))
    f1 = float(f1_score(y_t, y_p, zero_division=0))
    cm = confusion_matrix(y_t, y_p).tolist()
    
    roc_auc = float(roc_auc_score(y_t, y_prob[mask])) if y_prob is not None else None
    pr_auc = float(average_precision_score(y_t, y_prob[mask])) if y_prob is not None else None
    
    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "confusion_matrix": cm,
        "count": int(len(y_t)),
        "pos_count": int(y_t.sum()),
        "neg_count": int(len(y_t) - y_t.sum())
    }

def run_baselines():
    print("Loading data for empirical baselines...")
    df = pd.read_parquet(FEATURES_PARQUET)
    df["date_of_record"] = pd.to_datetime(df["date_of_record"])
    with open(SPLIT_MANIFEST, "r") as f:
        manifest = json.load(f)

    splits = {
        "fold1_val": ("2023-01-01", "2023-12-31"),
        "fold2_val": ("2024-01-01", "2024-12-31"),
        "holdout": ("2025-01-01", "2025-02-10")
    }

    results = {"target_a_temperature": {}, "target_b_rainfall_amount": {}, "target_c_rain_binary": {}}

    for split_name, (start_dt, end_dt) in splits.items():
        sub = df[(df["date_of_record"] >= start_dt) & (df["date_of_record"] <= end_dt)].copy()
        
        # Target A: Persistence prediction(t+1) = temperature(t)
        # We use avg_temp_clean(t) as predictor for target_next_day_temp
        y_true_a = sub["target_next_day_temp"].values
        y_pred_a = sub["avg_temp_clean"].values
        results["target_a_temperature"][split_name] = compute_regression_metrics(y_true_a, y_pred_a)
        
        # Target B: Rainfall amount persistence prediction(t+1) = rainfall(t)
        # Note: missing rainfall targets are strictly excluded
        valid_b = sub[sub["target_next_day_rainfall_amount"].notna()]
        y_true_b = valid_b["target_next_day_rainfall_amount"].values
        y_pred_b = valid_b["rainfall"].fillna(0.0).values # If day t rainfall is missing, assume 0 for persistence
        results["target_b_rainfall_amount"][split_name] = compute_regression_metrics(y_true_b, y_pred_b)
        
        # Target B on Rainy-Only days (y_true > 0)
        rainy_b = valid_b[valid_b["target_next_day_rainfall_amount"] > 0]
        results["target_b_rainfall_amount"][f"{split_name}_rainy_only"] = compute_regression_metrics(
            rainy_b["target_next_day_rainfall_amount"].values,
            rainy_b["rainfall"].fillna(0.0).values
        )

        # Target C: Rain/No-Rain majority class baseline (predict 0 = no rain)
        valid_c = sub[sub["target_next_day_rain_binary"].notna()]
        y_true_c = valid_c["target_next_day_rain_binary"].values
        y_pred_c = np.zeros(len(y_true_c)) # Majority class (dry)
        # Probability for majority baseline: historical training frequency of rain
        # For Fold 1 train (2021-2022), rain frequency is ~0.485
        prob_c = np.full(len(y_true_c), 0.485)
        results["target_c_rain_binary"][split_name] = compute_classification_metrics(y_true_c, y_pred_c, prob_c)

    output_file = OUTPUT_DIR / "baseline_metrics.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Empirical baselines evaluated and saved to {output_file}:")
    print(json.dumps(results, indent=2))
    return results

if __name__ == "__main__":
    run_baselines()
