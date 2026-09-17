import json
import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import matplotlib.pyplot as plt
from pathlib import Path

import model_config as cfg
from data_loaders import prepare_xgboost_data, get_holdout_data

def train_and_evaluate_xgboost(fold_id=1, task="regression"):
    """
    Trains XGBoost model for a given task (regression/classification) and fold.
    Saves the model and returns validation metrics.
    """
    print(f"--- Training XGBoost for {task.upper()} (Fold {fold_id}) ---")
    
    target = cfg.TARGET_TEMP if task == "regression" else cfg.TARGET_RAIN_BIN
    X_train, y_train, X_val, y_val = prepare_xgboost_data(fold_id=fold_id, target=target)
    
    if task == "regression":
        model = xgb.XGBRegressor(**cfg.XGB_CONFIG["temp_regressor"])
    else:
        # Calculate scale_pos_weight
        pos_count = y_train.sum()
        neg_count = len(y_train) - pos_count
        scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1.0
        
        config = cfg.XGB_CONFIG["rain_classifier"].copy()
        config["scale_pos_weight"] = scale_pos_weight
        model = xgb.XGBClassifier(**config)

    print(f"Train shape: {X_train.shape}, Val shape: {X_val.shape}")

    # Train model
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    
    # Evaluate
    preds = model.predict(X_val)
    metrics = evaluate_predictions(y_val, preds, task)
    
    print(f"Validation Metrics: {metrics}")
    
    # Save model
    model_path = cfg.MODELS_DIR / "xgboost" / f"xgb_{task}_fold{fold_id}.json"
    model.save_model(model_path)
    
    # Save feature importance
    plot_feature_importance(model, task, fold_id)
    
    return metrics, model

def evaluate_predictions(y_true, y_pred, task="regression"):
    if task == "regression":
        return {
            "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "mae": float(mean_absolute_error(y_true, y_pred)),
            "r2": float(r2_score(y_true, y_pred))
        }
    else:
        # For classification, we assume probabilities were NOT returned by predict for metric calc
        return {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_true, y_pred))
        }

def plot_feature_importance(model, task, fold_id):
    """Plots and saves feature importance."""
    importance = model.feature_importances_
    features = cfg.FEATURE_COLS
    
    df_imp = pd.DataFrame({'feature': features, 'importance': importance})
    df_imp = df_imp.sort_values('importance', ascending=False).head(15)
    
    plt.figure(figsize=(10, 6))
    plt.barh(df_imp['feature'][::-1], df_imp['importance'][::-1])
    plt.title(f"Top 15 Features for XGBoost {task.capitalize()} (Fold {fold_id})")
    plt.tight_layout()
    plt.savefig(cfg.RESULTS_DIR / "plots" / f"xgb_feat_imp_{task}_fold{fold_id}.png")
    plt.close()

if __name__ == "__main__":
    # Test execution
    train_and_evaluate_xgboost(fold_id=1, task="regression")
    train_and_evaluate_xgboost(fold_id=1, task="classification")
