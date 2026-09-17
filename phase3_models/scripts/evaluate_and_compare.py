import json
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(r"d:\weather_forcasting\phase3_models")
METRICS_DIR = BASE_DIR / "metrics"

def create_unified_metrics_registry():
    print("Consolidating metrics into unified metrics_summary.json...")
    
    with open(METRICS_DIR / "baseline_metrics.json", "r") as f:
        baseline_metrics = json.load(f)
    
    with open(METRICS_DIR / "xgboost_metrics.json", "r") as f:
        xgb_metrics = json.load(f)
        
    lstm_metrics_path = METRICS_DIR / "lstm_metrics.json"
    if lstm_metrics_path.exists():
        with open(lstm_metrics_path, "r") as f:
            lstm_metrics = json.load(f)
    else:
        lstm_metrics = {}

    unified = {
        "metadata": {
            "phase": "Phase 3 Forecasting Model Development",
            "authoritative_source_hash": "e6a636777430f078b4d970f9f46e79efcece7f97b67dd186c30a755d2783cd84",
            "cross_validation_strategy": "Chronological Walk-Forward Expanding Window",
            "holdout_period": "2025-01-01 to 2025-02-10",
            "models_compared": ["Baseline", "XGBoost", "LSTM"],
            "targets": ["Target A (Temperature)", "Target B (Rainfall Amount)", "Target C (Rain Binary)"]
        },
        "target_a_temperature": {
            "baseline": baseline_metrics.get("target_a_temperature", {}),
            "xgboost": xgb_metrics.get("target_a_temperature", {}),
            "lstm": lstm_metrics.get("target_a_temperature", {})
        },
        "target_b_rainfall_amount": {
            "baseline": baseline_metrics.get("target_b_rainfall_amount", {}),
            "xgboost": xgb_metrics.get("target_b_rainfall_amount", {}),
            "lstm": lstm_metrics.get("target_b_rainfall_amount", {})
        },
        "target_c_rain_binary": {
            "baseline": baseline_metrics.get("target_c_rain_binary", {}),
            "xgboost": xgb_metrics.get("target_c_rain_binary", {}),
            "lstm": lstm_metrics.get("target_c_rain_binary", {})
        }
    }

    out_path = METRICS_DIR / "metrics_summary.json"
    with open(out_path, "w") as f:
        json.dump(unified, f, indent=2)
        
    print(f"Unified metrics saved to {out_path}")
    return unified

def create_model_registry():
    print("Generating model_registry.json...")
    registry = {
        "version": "1.0.0",
        "phase": "Phase 3",
        "created_at": "2026-09-13",
        "models": [
            {
                "model_id": "xgb_temp_fold2_v1",
                "model_family": "XGBoost",
                "target": "target_next_day_temp",
                "task": "regression",
                "artifact_path": "phase3_models/xgboost/temperature/xgb_temp_fold2.json",
                "training_period": "2021-01-01 to 2023-12-31",
                "validation_period": "2024-01-01 to 2024-12-31",
                "status": "APPROVED_FOR_PRODUCTION_CANDIDATE"
            },
            {
                "model_id": "xgb_rain_amt_fold2_v1",
                "model_family": "XGBoost",
                "target": "target_next_day_rainfall_amount",
                "task": "regression",
                "artifact_path": "phase3_models/xgboost/rainfall/xgb_rain_amt_fold2.json",
                "transformation": "log1p",
                "training_period": "2021-01-01 to 2023-12-31",
                "validation_period": "2024-01-01 to 2024-12-31",
                "status": "APPROVED_FOR_PRODUCTION_CANDIDATE"
            },
            {
                "model_id": "xgb_rain_cls_fold2_v1",
                "model_family": "XGBoost",
                "target": "target_next_day_rain_binary",
                "task": "binary_classification",
                "artifact_path": "phase3_models/xgboost/rain_classification/xgb_rain_cls_fold2.json",
                "training_period": "2021-01-01 to 2023-12-31",
                "validation_period": "2024-01-01 to 2024-12-31",
                "status": "APPROVED_FOR_PRODUCTION_CANDIDATE"
            },
            {
                "model_id": "lstm_temp_fold2_v1",
                "model_family": "LSTM",
                "target": "target_next_day_temp",
                "task": "regression",
                "artifact_path": "phase3_models/lstm/temperature/lstm_temperature_fold2.pt",
                "preprocessor_path": "phase3_models/preprocessors/scaler_lstm_temperature_fold2.joblib",
                "sequence_length": 7,
                "training_period": "2021-01-01 to 2023-12-31",
                "validation_period": "2024-01-01 to 2024-12-31",
                "status": "BENCHMARKED"
            },
            {
                "model_id": "lstm_rain_amt_fold2_v1",
                "model_family": "LSTM",
                "target": "target_next_day_rainfall_amount",
                "task": "regression",
                "artifact_path": "phase3_models/lstm/rainfall/lstm_rainfall_fold2.pt",
                "preprocessor_path": "phase3_models/preprocessors/scaler_lstm_rainfall_fold2.joblib",
                "transformation": "log1p",
                "sequence_length": 7,
                "training_period": "2021-01-01 to 2023-12-31",
                "validation_period": "2024-01-01 to 2024-12-31",
                "status": "BENCHMARKED"
            },
            {
                "model_id": "lstm_rain_cls_fold2_v1",
                "model_family": "LSTM",
                "target": "target_next_day_rain_binary",
                "task": "binary_classification",
                "artifact_path": "phase3_models/lstm/rain_classification/lstm_rain_classification_fold2.pt",
                "preprocessor_path": "phase3_models/preprocessors/scaler_lstm_rain_classification_fold2.joblib",
                "sequence_length": 7,
                "training_period": "2021-01-01 to 2023-12-31",
                "validation_period": "2024-01-01 to 2024-12-31",
                "status": "BENCHMARKED"
            }
        ]
    }
    
    out_file = BASE_DIR / "model_registry.json"
    with open(out_file, "w") as f:
        json.dump(registry, f, indent=2)
    print(f"Model registry saved to {out_file}")

if __name__ == "__main__":
    create_unified_metrics_registry()
    create_model_registry()
