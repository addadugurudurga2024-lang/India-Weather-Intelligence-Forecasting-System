import os
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import xgboost as xgb
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
import matplotlib.pyplot as plt

FEATURES_PARQUET = Path(r"d:\weather_forcasting\phase2_canonical\outputs\features_engineered.parquet")
BASE_DIR = Path(r"d:\weather_forcasting\phase3_models")
XGB_DIR = BASE_DIR / "xgboost"
PRED_DIR = BASE_DIR / "predictions"
METRICS_DIR = BASE_DIR / "metrics"
PLOTS_DIR = BASE_DIR / "plots"

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

def load_data():
    print("Loading engineered features...")
    df = pd.read_parquet(FEATURES_PARQUET)
    df["date_of_record"] = pd.to_datetime(df["date_of_record"])
    return df

def train_xgboost_temperature(df):
    print("\n=======================================================")
    print("TASK 08: XGBoost Temperature Regression (Target A)")
    print("=======================================================")
    target = "target_next_day_temp"
    results = {}
    
    # Track models across folds
    trained_models = {}

    for fold_name, dates in FOLDS.items():
        print(f"--- Training {fold_name.upper()} ---")
        train_df = df[(df["date_of_record"] >= dates["train"][0]) & (df["date_of_record"] <= dates["train"][1])].copy()
        val_df = df[(df["date_of_record"] >= dates["val"][0]) & (df["date_of_record"] <= dates["val"][1])].copy()
        
        train_df = train_df.dropna(subset=[target])
        val_df = val_df.dropna(subset=[target])
        
        X_train, y_train = train_df[FEATURES], train_df[target]
        X_val, y_val = val_df[FEATURES], val_df[target]

        t0 = time.time()
        model = xgb.XGBRegressor(
            n_estimators=600,
            learning_rate=0.04,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            early_stopping_rounds=40,
            random_state=42,
            n_jobs=-1,
            tree_method="hist"
        )
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=100
        )
        train_time = round(time.time() - t0, 2)
        
        val_preds = model.predict(X_val)
        mae = float(mean_absolute_error(y_val, val_preds))
        rmse = float(np.sqrt(mean_squared_error(y_val, val_preds)))
        r2 = float(r2_score(y_val, val_preds))
        
        results[fold_name] = {
            "mae": mae, "rmse": rmse, "r2": r2,
            "train_rows": len(X_train), "val_rows": len(X_val),
            "train_time_sec": train_time, "best_iteration": int(model.best_iteration)
        }
        print(f"{fold_name.upper()} Results: MAE={mae:.4f}, RMSE={rmse:.4f}, R2={r2:.4f}, Time={train_time}s")
        
        # Save model
        save_path = XGB_DIR / "temperature" / f"xgb_temp_{fold_name}.json"
        model.save_model(str(save_path))
        trained_models[fold_name] = model
        
        # Save validation predictions
        pred_df = val_df[["station_id", "date_of_record"]].copy()
        pred_df["actual"] = y_val.values
        pred_df["predicted"] = val_preds
        pred_df["split"] = f"{fold_name}_val"
        pred_df["model"] = "xgboost"
        pred_df["target"] = target
        pred_df.to_parquet(PRED_DIR / f"xgb_temp_preds_{fold_name}.parquet", index=False)

    # Evaluate best fold model on Holdout
    holdout_df = df[(df["date_of_record"] >= HOLDOUT_PERIOD[0]) & (df["date_of_record"] <= HOLDOUT_PERIOD[1])].dropna(subset=[target]).copy()
    X_holdout, y_holdout = holdout_df[FEATURES], holdout_df[target]
    
    # Use Fold 2 model (trained on 2021-2023) for holdout evaluation
    best_model = trained_models["fold2"]
    holdout_preds = best_model.predict(X_holdout)
    results["holdout"] = {
        "mae": float(mean_absolute_error(y_holdout, holdout_preds)),
        "rmse": float(np.sqrt(mean_squared_error(y_holdout, holdout_preds))),
        "r2": float(r2_score(y_holdout, holdout_preds)),
        "holdout_rows": len(X_holdout)
    }
    print(f"HOLDOUT Results: MAE={results['holdout']['mae']:.4f}, RMSE={results['holdout']['rmse']:.4f}, R2={results['holdout']['r2']:.4f}")
    
    # Save holdout predictions
    hold_pred_df = holdout_df[["station_id", "date_of_record"]].copy()
    hold_pred_df["actual"] = y_holdout.values
    hold_pred_df["predicted"] = holdout_preds
    hold_pred_df["split"] = "holdout_2025"
    hold_pred_df["model"] = "xgboost"
    hold_pred_df["target"] = target
    hold_pred_df.to_parquet(PRED_DIR / "xgb_temp_preds_holdout.parquet", index=False)

    # Plot top 15 feature importances
    feat_imp = pd.Series(best_model.feature_importances_, index=FEATURES).sort_values(ascending=False).head(15)
    plt.figure(figsize=(10, 6))
    feat_imp.iloc[::-1].plot(kind="barh", color="#1f77b4")
    plt.title("XGBoost Temperature Feature Importance (Gain / Split)")
    plt.xlabel("Importance")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "xgb_temp_feature_importance.png", dpi=150)
    plt.close()

    return results

def train_xgboost_rainfall_amount(df):
    print("\n=======================================================")
    print("TASK 09: XGBoost Rainfall Amount Regression (Target B)")
    print("=======================================================")
    target = "target_next_day_rainfall_amount"
    results = {}
    trained_models = {}

    for fold_name, dates in FOLDS.items():
        print(f"--- Training {fold_name.upper()} (log1p transform) ---")
        train_df = df[(df["date_of_record"] >= dates["train"][0]) & (df["date_of_record"] <= dates["train"][1])].dropna(subset=[target]).copy()
        val_df = df[(df["date_of_record"] >= dates["val"][0]) & (df["date_of_record"] <= dates["val"][1])].dropna(subset=[target]).copy()
        
        X_train, y_train = train_df[FEATURES], np.log1p(train_df[target].values)
        X_val, y_val_raw = val_df[FEATURES], val_df[target].values
        y_val_log = np.log1p(y_val_raw)

        t0 = time.time()
        model = xgb.XGBRegressor(
            n_estimators=600,
            learning_rate=0.04,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            early_stopping_rounds=40,
            random_state=42,
            n_jobs=-1,
            tree_method="hist"
        )
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val_log)],
            verbose=100
        )
        train_time = round(time.time() - t0, 2)
        
        pred_log = model.predict(X_val)
        val_preds = np.expm1(np.clip(pred_log, 0, None)) # Inverse transform back to mm
        
        mae = float(mean_absolute_error(y_val_raw, val_preds))
        rmse = float(np.sqrt(mean_squared_error(y_val_raw, val_preds)))
        r2 = float(r2_score(y_val_raw, val_preds))
        
        # Rainy only performance
        rainy_mask = y_val_raw > 0
        mae_rainy = float(mean_absolute_error(y_val_raw[rainy_mask], val_preds[rainy_mask]))
        rmse_rainy = float(np.sqrt(mean_squared_error(y_val_raw[rainy_mask], val_preds[rainy_mask])))
        
        results[fold_name] = {
            "mae": mae, "rmse": rmse, "r2": r2,
            "mae_rainy_only": mae_rainy, "rmse_rainy_only": rmse_rainy,
            "train_rows": len(X_train), "val_rows": len(X_val),
            "train_time_sec": train_time, "best_iteration": int(model.best_iteration)
        }
        print(f"{fold_name.upper()} Overall: MAE={mae:.4f}mm, RMSE={rmse:.4f}mm, R2={r2:.4f}")
        print(f"{fold_name.upper()} Rainy-Only: MAE={mae_rainy:.4f}mm, RMSE={rmse_rainy:.4f}mm")

        # Save model
        save_path = XGB_DIR / "rainfall" / f"xgb_rain_amt_{fold_name}.json"
        model.save_model(str(save_path))
        trained_models[fold_name] = model

        # Save predictions
        pred_df = val_df[["station_id", "date_of_record"]].copy()
        pred_df["actual"] = y_val_raw
        pred_df["predicted"] = val_preds
        pred_df["split"] = f"{fold_name}_val"
        pred_df["model"] = "xgboost"
        pred_df["target"] = target
        pred_df.to_parquet(PRED_DIR / f"xgb_rain_preds_{fold_name}.parquet", index=False)

    # Evaluate on Holdout
    holdout_df = df[(df["date_of_record"] >= HOLDOUT_PERIOD[0]) & (df["date_of_record"] <= HOLDOUT_PERIOD[1])].dropna(subset=[target]).copy()
    X_holdout, y_holdout_raw = holdout_df[FEATURES], holdout_df[target].values
    best_model = trained_models["fold2"]
    hold_pred_log = best_model.predict(X_holdout)
    holdout_preds = np.expm1(np.clip(hold_pred_log, 0, None))
    
    mae_h = float(mean_absolute_error(y_holdout_raw, holdout_preds))
    rmse_h = float(np.sqrt(mean_squared_error(y_holdout_raw, holdout_preds)))
    r2_h = float(r2_score(y_holdout_raw, holdout_preds))
    rainy_h = y_holdout_raw > 0
    mae_h_rainy = float(mean_absolute_error(y_holdout_raw[rainy_h], holdout_preds[rainy_h]))
    rmse_h_rainy = float(np.sqrt(mean_squared_error(y_holdout_raw[rainy_h], holdout_preds[rainy_h])))
    
    results["holdout"] = {
        "mae": mae_h, "rmse": rmse_h, "r2": r2_h,
        "mae_rainy_only": mae_h_rainy, "rmse_rainy_only": rmse_h_rainy,
        "holdout_rows": len(X_holdout)
    }
    print(f"HOLDOUT Overall: MAE={mae_h:.4f}mm, RMSE={rmse_h:.4f}mm, R2={r2_h:.4f}")
    print(f"HOLDOUT Rainy-Only: MAE={mae_h_rainy:.4f}mm, RMSE={rmse_h_rainy:.4f}mm")

    hold_pred_df = holdout_df[["station_id", "date_of_record"]].copy()
    hold_pred_df["actual"] = y_holdout_raw
    hold_pred_df["predicted"] = holdout_preds
    hold_pred_df["split"] = "holdout_2025"
    hold_pred_df["model"] = "xgboost"
    hold_pred_df["target"] = target
    hold_pred_df.to_parquet(PRED_DIR / "xgb_rain_preds_holdout.parquet", index=False)

    return results

def train_xgboost_rain_classification(df):
    print("\n=======================================================")
    print("TASK 10: XGBoost Rain/No-Rain Classification (Target C)")
    print("=======================================================")
    target = "target_next_day_rain_binary"
    results = {}
    trained_models = {}

    for fold_name, dates in FOLDS.items():
        print(f"--- Training {fold_name.upper()} ---")
        train_df = df[(df["date_of_record"] >= dates["train"][0]) & (df["date_of_record"] <= dates["train"][1])].dropna(subset=[target]).copy()
        val_df = df[(df["date_of_record"] >= dates["val"][0]) & (df["date_of_record"] <= dates["val"][1])].dropna(subset=[target]).copy()
        
        X_train, y_train = train_df[FEATURES], train_df[target].astype(int)
        X_val, y_val = val_df[FEATURES], val_df[target].astype(int)
        
        pos_cnt = int(y_train.sum())
        neg_cnt = int(len(y_train) - pos_cnt)
        scale_pos = neg_cnt / pos_cnt if pos_cnt > 0 else 1.0
        
        t0 = time.time()
        model = xgb.XGBClassifier(
            n_estimators=600,
            learning_rate=0.04,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos,
            early_stopping_rounds=40,
            random_state=42,
            n_jobs=-1,
            eval_metric="logloss",
            tree_method="hist"
        )
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=100
        )
        train_time = round(time.time() - t0, 2)
        
        val_probs = model.predict_proba(X_val)[:, 1]
        val_preds = (val_probs >= 0.5).astype(int)
        
        acc = float(accuracy_score(y_val, val_preds))
        prec = float(precision_score(y_val, val_preds, zero_division=0))
        rec = float(recall_score(y_val, val_preds, zero_division=0))
        f1 = float(f1_score(y_val, val_preds, zero_division=0))
        roc_auc = float(roc_auc_score(y_val, val_probs))
        pr_auc = float(average_precision_score(y_val, val_probs))
        cm = confusion_matrix(y_val, val_preds).tolist()
        
        results[fold_name] = {
            "accuracy": acc, "precision": prec, "recall": rec, "f1": f1,
            "roc_auc": roc_auc, "pr_auc": pr_auc, "confusion_matrix": cm,
            "train_rows": len(X_train), "val_rows": len(X_val),
            "train_time_sec": train_time, "best_iteration": int(model.best_iteration)
        }
        print(f"{fold_name.upper()} Accuracy={acc:.4f}, Precision={prec:.4f}, Recall={rec:.4f}, F1={f1:.4f}, ROC-AUC={roc_auc:.4f}, PR-AUC={pr_auc:.4f}")

        save_path = XGB_DIR / "rain_classification" / f"xgb_rain_cls_{fold_name}.json"
        model.save_model(str(save_path))
        trained_models[fold_name] = model

        pred_df = val_df[["station_id", "date_of_record"]].copy()
        pred_df["actual"] = y_val.values
        pred_df["predicted"] = val_preds
        pred_df["probability"] = val_probs
        pred_df["threshold"] = 0.5
        pred_df["split"] = f"{fold_name}_val"
        pred_df["model"] = "xgboost"
        pred_df["target"] = target
        pred_df.to_parquet(PRED_DIR / f"xgb_rain_cls_preds_{fold_name}.parquet", index=False)

    # Holdout
    holdout_df = df[(df["date_of_record"] >= HOLDOUT_PERIOD[0]) & (df["date_of_record"] <= HOLDOUT_PERIOD[1])].dropna(subset=[target]).copy()
    X_holdout, y_holdout = holdout_df[FEATURES], holdout_df[target].astype(int)
    best_model = trained_models["fold2"]
    hold_probs = best_model.predict_proba(X_holdout)[:, 1]
    hold_preds = (hold_probs >= 0.5).astype(int)
    
    results["holdout"] = {
        "accuracy": float(accuracy_score(y_holdout, hold_preds)),
        "precision": float(precision_score(y_holdout, hold_preds, zero_division=0)),
        "recall": float(recall_score(y_holdout, hold_preds, zero_division=0)),
        "f1": float(f1_score(y_holdout, hold_preds, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_holdout, hold_probs)),
        "pr_auc": float(average_precision_score(y_holdout, hold_probs)),
        "confusion_matrix": confusion_matrix(y_holdout, hold_preds).tolist(),
        "holdout_rows": len(X_holdout)
    }
    print(f"HOLDOUT Accuracy={results['holdout']['accuracy']:.4f}, Precision={results['holdout']['precision']:.4f}, Recall={results['holdout']['recall']:.4f}, F1={results['holdout']['f1']:.4f}, ROC-AUC={results['holdout']['roc_auc']:.4f}")

    hold_pred_df = holdout_df[["station_id", "date_of_record"]].copy()
    hold_pred_df["actual"] = y_holdout.values
    hold_pred_df["predicted"] = hold_preds
    hold_pred_df["probability"] = hold_probs
    hold_pred_df["threshold"] = 0.5
    hold_pred_df["split"] = "holdout_2025"
    hold_pred_df["model"] = "xgboost"
    hold_pred_df["target"] = target
    hold_pred_df.to_parquet(PRED_DIR / "xgb_rain_cls_preds_holdout.parquet", index=False)

    return results

def main():
    df = load_data()
    all_xgb_results = {}
    all_xgb_results["target_a_temperature"] = train_xgboost_temperature(df)
    all_xgb_results["target_b_rainfall_amount"] = train_xgboost_rainfall_amount(df)
    all_xgb_results["target_c_rain_binary"] = train_xgboost_rain_classification(df)
    
    with open(METRICS_DIR / "xgboost_metrics.json", "w") as f:
        json.dump(all_xgb_results, f, indent=2)
    print("\nAll XGBoost models trained and metrics saved successfully!")

if __name__ == "__main__":
    main()
