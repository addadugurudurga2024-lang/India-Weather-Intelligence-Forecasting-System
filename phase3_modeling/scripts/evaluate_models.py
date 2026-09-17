import json
import torch
import xgboost as xgb
import numpy as np
import pandas as pd
from pathlib import Path

import model_config as cfg
from data_loaders import get_holdout_data, get_lstm_dataloaders
from train_xgboost import evaluate_predictions as evaluate_xgb
from train_lstm import WeatherLSTM, evaluate_predictions as evaluate_lstm

def evaluate_xgboost_holdout(task="regression", fold_id=1):
    target = cfg.TARGET_TEMP if task == "regression" else cfg.TARGET_RAIN_BIN
    X_test, y_test = get_holdout_data(target=target)
    
    model_path = cfg.MODELS_DIR / "xgboost" / f"xgb_{task}_fold{fold_id}.json"
    
    if task == "regression":
        model = xgb.XGBRegressor()
    else:
        model = xgb.XGBClassifier()
        
    model.load_model(model_path)
    
    preds = model.predict(X_test)
    metrics = evaluate_xgb(y_test, preds, task)
    return metrics

def evaluate_lstm_holdout(task="regression", fold_id=1):
    target = cfg.TARGET_TEMP if task == "regression" else cfg.TARGET_RAIN_BIN
    
    # We need to construct DataLoader for holdout just like we did for train/val
    # To do this correctly, we will reuse data_loaders logic but for holdout
    # Since holdout uses TimeSeriesDataset, we need to load the dataframe and pass it.
    
    from data_loaders import load_data, TimeSeriesDataset
    from torch.utils.data import DataLoader
    
    df, manifest = load_data()
    holdout_start = manifest["holdout_test_set"]["period"]["start"]
    holdout_end = manifest["holdout_test_set"]["period"]["end"]
    
    test_df = df[(df["date_of_record"] >= holdout_start) & (df["date_of_record"] <= holdout_end)].copy()
    test_df[cfg.FEATURE_COLS] = test_df[cfg.FEATURE_COLS].fillna(0)
    
    test_dataset = TimeSeriesDataset(test_df, cfg.FEATURE_COLS, target, cfg.LSTM_CONFIG["sequence_length"])
    test_loader = DataLoader(test_dataset, batch_size=cfg.LSTM_CONFIG["batch_size"], shuffle=False)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    input_size = len(cfg.FEATURE_COLS)
    
    model = WeatherLSTM(
        input_size=input_size,
        hidden_size=cfg.LSTM_CONFIG["hidden_size"],
        num_layers=cfg.LSTM_CONFIG["num_layers"],
        dropout=cfg.LSTM_CONFIG["dropout"],
        task=task
    ).to(device)
    
    model_path = cfg.MODELS_DIR / "lstm" / f"lstm_{task}_fold{fold_id}.pt"
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    model.eval()
    
    all_preds = []
    all_targets = []
    
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            preds = model(X_batch)
            if task == "classification":
                probs = torch.sigmoid(preds)
                binary_preds = (probs > 0.5).float()
                all_preds.extend(binary_preds.cpu().numpy())
            else:
                all_preds.extend(preds.cpu().numpy())
            all_targets.extend(y_batch.cpu().numpy())
            
    metrics = evaluate_lstm(all_targets, all_preds, task)
    return metrics

def run_evaluation():
    results = {}
    
    print("Evaluating XGBoost models on Holdout Test Set (2025)...")
    results["xgboost_regression_fold1"] = evaluate_xgboost_holdout("regression", 1)
    results["xgboost_regression_fold2"] = evaluate_xgboost_holdout("regression", 2)
    results["xgboost_classification_fold1"] = evaluate_xgboost_holdout("classification", 1)
    results["xgboost_classification_fold2"] = evaluate_xgboost_holdout("classification", 2)
    
    print("Evaluating LSTM models on Holdout Test Set (2025)...")
    results["lstm_regression_fold1"] = evaluate_lstm_holdout("regression", 1)
    results["lstm_regression_fold2"] = evaluate_lstm_holdout("regression", 2)
    results["lstm_classification_fold1"] = evaluate_lstm_holdout("classification", 1)
    results["lstm_classification_fold2"] = evaluate_lstm_holdout("classification", 2)
    
    with open(cfg.RESULTS_DIR / "metrics_summary.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print("Evaluation completed. Results saved to metrics_summary.json")

if __name__ == "__main__":
    run_evaluation()
