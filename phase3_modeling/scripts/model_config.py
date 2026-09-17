import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path("d:/weather_forcasting")
PHASE2_OUTPUT_DIR = PROJECT_ROOT / "phase2_canonical" / "outputs"
PHASE3_DIR = PROJECT_ROOT / "phase3_modeling"

DATA_PATH = PHASE2_OUTPUT_DIR / "features_engineered.parquet"
SPLIT_MANIFEST_PATH = PHASE2_OUTPUT_DIR / "temporal_split_manifest.json"

MODELS_DIR = PHASE3_DIR / "models"
RESULTS_DIR = PHASE3_DIR / "results"
REPORTS_DIR = PHASE3_DIR / "reports"

# Ensure dirs exist
for d in [MODELS_DIR / "xgboost", MODELS_DIR / "lstm", RESULTS_DIR / "plots", REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Targets
TARGET_TEMP = "target_next_day_temp"
TARGET_RAIN_BIN = "target_next_day_rain_binary"
TARGET_RAIN_AMT = "target_next_day_rainfall_amount"

# Features
METADATA_COLS = ["date_of_record", "station_name", "state", "district", "station_id", "qc_flag_temp"]

# Base clean features (using the non-lagged as current day features where appropriate)
CURRENT_DAY_FEATURES = [
    "avg_temp_clean", "min_temp_clean", "max_temp_clean", 
    "wind_speed", "air_pressure", "rainfall",
    "elevation", "latitude", "longitude"
]

CYCLICAL_FEATURES = ["doy_sin", "doy_cos", "month_sin", "month_cos"]

LAG_FEATURES = [
    "lag_1_avg_temp", "lag_2_avg_temp", "lag_1_min_temp", "lag_1_max_temp",
    "lag_1_rainfall", "lag_2_rainfall", "lag_1_wind_speed", "lag_1_air_pressure"
]

ROLLING_FEATURES = [
    "rolling_3d_temp_mean", "rolling_7d_temp_mean", "rolling_7d_temp_std",
    "rolling_3d_rainfall_sum", "rolling_7d_rainfall_sum"
]

CATEGORICAL_FEATURES = ["month", "season"]

# All input features for modeling (using cyclical instead of string categorical)
FEATURE_COLS = CURRENT_DAY_FEATURES + CYCLICAL_FEATURES + LAG_FEATURES + ROLLING_FEATURES

# XGBoost Hyperparameters
XGB_CONFIG = {
    "temp_regressor": {
        "n_estimators": 500,
        "learning_rate": 0.05,
        "max_depth": 6,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "early_stopping_rounds": 50,
        "random_state": 42,
        "n_jobs": -1
    },
    "rain_classifier": {
        "n_estimators": 500,
        "learning_rate": 0.05,
        "max_depth": 6,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "scale_pos_weight": 1.0, # Will be updated dynamically based on class balance
        "early_stopping_rounds": 50,
        "random_state": 42,
        "n_jobs": -1,
        "eval_metric": "logloss"
    }
}

# LSTM Hyperparameters
LSTM_CONFIG = {
    "sequence_length": 7,
    "batch_size": 2048,
    "hidden_size": 64,
    "num_layers": 2,
    "dropout": 0.2,
    "learning_rate": 0.001,
    "epochs": 50,
    "patience": 10
}
