import json
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(r"d:\weather_forcasting\phase3_models")
XGB_DIR = BASE_DIR / "xgboost"
LSTM_DIR = BASE_DIR / "lstm"
PREPROC_DIR = BASE_DIR / "preprocessors"
PRED_DIR = BASE_DIR / "predictions"
METRICS_DIR = BASE_DIR / "metrics"
PLOTS_DIR = BASE_DIR / "plots"

def test_model_artifacts_exist():
    # XGBoost models
    for fold in ["fold1", "fold2"]:
        assert (XGB_DIR / "temperature" / f"xgb_temp_{fold}.json").exists(), f"Missing xgb_temp_{fold}.json"
        assert (XGB_DIR / "rainfall" / f"xgb_rain_amt_{fold}.json").exists(), f"Missing xgb_rain_amt_{fold}.json"
        assert (XGB_DIR / "rain_classification" / f"xgb_rain_cls_{fold}.json").exists(), f"Missing xgb_rain_cls_{fold}.json"
        
    # LSTM models
    for fold in ["fold1", "fold2"]:
        assert (LSTM_DIR / "temperature" / f"lstm_temperature_{fold}.pt").exists(), f"Missing lstm_temp_{fold}.pt"
        assert (LSTM_DIR / "rainfall" / f"lstm_rainfall_{fold}.pt").exists(), f"Missing lstm_rainfall_{fold}.pt"
        assert (LSTM_DIR / "rain_classification" / f"lstm_rain_classification_{fold}.pt").exists(), f"Missing lstm_rain_cls_{fold}.pt"
        assert (PREPROC_DIR / f"scaler_lstm_temperature_{fold}.joblib").exists()

def test_predictions_exist_and_non_empty():
    for pred_file in [
        "xgb_temp_preds_holdout.parquet",
        "xgb_rain_preds_holdout.parquet",
        "xgb_rain_cls_preds_holdout.parquet",
        "lstm_temperature_preds_holdout.parquet",
        "lstm_rainfall_preds_holdout.parquet",
        "lstm_rain_classification_preds_holdout.parquet"
    ]:
        fpath = PRED_DIR / pred_file
        assert fpath.exists(), f"Missing prediction file: {pred_file}"
        df = pd.read_parquet(fpath)
        assert len(df) > 0, f"Empty prediction file: {pred_file}"
        assert "actual" in df.columns and "predicted" in df.columns

def test_metrics_integrity():
    metrics_path = METRICS_DIR / "metrics_summary.json"
    assert metrics_path.exists(), "Missing metrics_summary.json"
    with open(metrics_path, "r") as f:
        metrics = json.load(f)
        
    for target_key in ["target_a_temperature", "target_b_rainfall_amount", "target_c_rain_binary"]:
        assert target_key in metrics, f"Missing {target_key} in metrics summary"
        for family in ["baseline", "xgboost", "lstm"]:
            assert family in metrics[target_key], f"Missing {family} in {target_key}"
            holdout_res = metrics[target_key][family].get("holdout")
            assert holdout_res is not None, f"Missing holdout for {family} on {target_key}"
            if "regression" in target_key or "temperature" in target_key or "amount" in target_key:
                assert np.isfinite(holdout_res["mae"]) and holdout_res["mae"] > 0
                assert np.isfinite(holdout_res["rmse"]) and holdout_res["rmse"] > 0
            else:
                assert np.isfinite(holdout_res["accuracy"]) and 0 <= holdout_res["accuracy"] <= 1.0
                assert np.isfinite(holdout_res["f1"]) and 0 <= holdout_res["f1"] <= 1.0

def test_plots_exist():
    assert (PLOTS_DIR / "temp_eval_actual_vs_pred_residuals.png").exists()
    assert (PLOTS_DIR / "rain_amount_eval_scatter_and_error.png").exists()
    assert (PLOTS_DIR / "rain_cls_eval_cm_roc_pr.png").exists()

def test_model_registry_valid():
    reg_path = BASE_DIR / "model_registry.json"
    assert reg_path.exists(), "Missing model_registry.json"
    with open(reg_path, "r") as f:
        reg = json.load(f)
    assert "models" in reg and len(reg["models"]) >= 6

if __name__ == "__main__":
    print("Running test_phase3_suite...")
    test_model_artifacts_exist()
    test_predictions_exist_and_non_empty()
    test_metrics_integrity()
    test_plots_exist()
    test_model_registry_valid()
    print("ALL PHASE 3 AUTOMATED TESTS PASSED SUCCESSFULLY!")
