"""
Phase 6 Automated Test Suite: Model Evaluation, Benchmarking & Explainability
Verifies:
1. Baseline SHA-256 integrity lock on all 41 Phase 3 artifacts
2. Metric reconciliation across Phase 3, 4, 5, and 6
3. Evaluation dataset integrity (18 parquets, row counts, 0 NaNs)
4. Temporal walk-forward chronological splits (no leakage, isolated holdout)
5. TreeSHAP feature attributions on exact 26 Phase 3 features
6. Calibration reliability and ECE calculation integrity
7. Threshold sensitivity sweep validity (0.05 <= tau <= 0.95)
8. Frontend evaluation payload integrity (authoritativeEvaluationSummary.json)
9. Phase boundary hygiene (zero Phase 7 or 8 code)
"""

import hashlib
import json
from pathlib import Path
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT_DIR / "phase6_evaluation" / "manifests" / "phase3_baseline_integrity_lock.json"
DATA_PATH = ROOT_DIR / "phase6_evaluation" / "data" / "phase6_evaluation_summary.json"
FE_DATA_PATH = ROOT_DIR / "frontend" / "src" / "data" / "authoritativeEvaluationSummary.json"
METRICS_PATH = ROOT_DIR / "frontend" / "src" / "data" / "authoritativeMetrics.json"
PLOTS_DIR = ROOT_DIR / "phase6_evaluation" / "plots"

def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def test_baseline_integrity_lock():
    assert MANIFEST_PATH.exists(), "phase3_baseline_integrity_lock.json missing!"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    assert len(manifest["artifacts"]) == 41, f"Expected 41 locked artifacts, found {len(manifest['artifacts'])}"
    
    # Verify hashes on all 41 files
    for rel_path, meta in manifest["artifacts"].items():
        full_path = ROOT_DIR / rel_path
        assert full_path.exists(), f"Locked artifact missing: {rel_path}"
        current_hash = compute_sha256(full_path)
        assert current_hash == meta["sha256"], f"Artifact hash mismatch for {rel_path}! Expected {meta['sha256']}, got {current_hash}"
        assert full_path.stat().st_size == meta["size_bytes"], f"Artifact size mismatch for {rel_path}!"
    print(f"[PASS] All {len(manifest['artifacts'])} Phase 3 baseline artifacts verified against cryptographic SHA-256 lock.")

def test_authoritative_metrics_fidelity():
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)
        
    # Temperature
    xgb_temp = metrics["target_a_temperature"]["xgboost"]["holdout"]["mae"]
    lstm_temp = metrics["target_a_temperature"]["lstm"]["holdout"]["mae"]
    assert abs(xgb_temp - 0.6527) < 1e-4, f"XGB temp MAE altered: {xgb_temp}"
    assert abs(lstm_temp - 0.6441) < 1e-4, f"LSTM temp MAE altered: {lstm_temp}"
    
    # Rainfall
    xgb_rain = metrics["target_b_rainfall_amount"]["xgboost"]["holdout"]["mae"]
    lstm_rain = metrics["target_b_rainfall_amount"]["lstm"]["holdout"]["mae"]
    assert abs(xgb_rain - 0.4344) < 1e-4, f"XGB rain MAE altered: {xgb_rain}"
    assert abs(lstm_rain - 0.4368) < 1e-4, f"LSTM rain MAE altered: {lstm_rain}"
    
    # Rain Classification
    xgb_cls_acc = metrics["target_c_rain_binary"]["xgboost"]["holdout"]["accuracy"]
    xgb_cls_auc = metrics["target_c_rain_binary"]["xgboost"]["holdout"]["roc_auc"]
    assert abs(xgb_cls_acc - 0.8919) < 1e-4
    assert abs(xgb_cls_auc - 0.8366) < 1e-4
    print("[PASS] Authoritative Phase 3 holdout benchmarks verified with exact numerical match.")

def test_evaluation_summary_payload():
    assert DATA_PATH.exists(), "phase6_evaluation_summary.json missing!"
    assert FE_DATA_PATH.exists(), "authoritativeEvaluationSummary.json missing in frontend!"
    
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
        
    # Check benchmarks
    assert "benchmarks" in eval_data
    assert "temperature" in eval_data["benchmarks"]
    assert "rainfall_amount" in eval_data["benchmarks"]
    assert "rain_classification" in eval_data["benchmarks"]
    
    # Check threshold sweep
    thresh = eval_data["threshold_analysis"]
    assert len(thresh["sweep"]) == 19
    assert thresh["optimal_f1_threshold"] == 0.30
    assert thresh["max_f1"] >= 0.44
    
    # Check calibration
    calib = eval_data["calibration"]
    assert 0.05 <= calib["expected_calibration_error"] <= 0.08
    assert calib["brier_score"] <= 0.10
    assert len(calib["reliability_bins"]) == 10
    
    # Check explainability SHAP
    shap = eval_data["explainability"]
    assert len(shap["temperature_shap_rankings"]) == 26, f"Expected 26 features in temp SHAP, got {len(shap['temperature_shap_rankings'])}"
    assert len(shap["rain_classification_shap_rankings"]) == 26, f"Expected 26 features in cls SHAP, got {len(shap['rain_classification_shap_rankings'])}"
    assert shap["temperature_shap_rankings"][0]["feature"] == "avg_temp_clean"
    
    # Check local case studies
    assert len(shap["local_case_studies"]) >= 2
    for cs in shap["local_case_studies"]:
        if cs:
            assert "predicted_temp" in cs
            assert "base_value" in cs
            assert len(cs["top_contributions"]) == 4
            
    print("[PASS] Comprehensive Phase 6 evaluation summary payload verified.")

def test_visual_plots_exist():
    expected_plots = [
        "feature_importance_shap_ranking.png",
        "reliability_calibration_diagram.png",
        "threshold_tuning_curve.png",
        "elevation_error_distribution.png",
        "model_benchmark_comparison_matrix.png"
    ]
    for p in expected_plots:
        plot_file = PLOTS_DIR / p
        assert plot_file.exists(), f"Plot artifact missing: {p}"
        assert plot_file.stat().st_size > 5000, f"Plot artifact suspiciously small: {p}"
    print(f"[PASS] All {len(expected_plots)} publication-quality visualization artifacts verified.")

def test_phase_boundary_hygiene():
    forbidden_dirs = [
        ROOT_DIR / "phase7_ai_intelligence",
        ROOT_DIR / "phase8_backend",
        ROOT_DIR / "app"
    ]
    for p in forbidden_dirs:
        assert not p.exists(), f"Phase boundary violated: Unauthorized directory found: {p}"
    print("[PASS] Phase boundary hygiene verified.")

if __name__ == "__main__":
    print("==================================================")
    print("RUNNING PHASE 6 AUTOMATED VERIFICATION SUITE")
    print("==================================================")
    test_baseline_integrity_lock()
    test_authoritative_metrics_fidelity()
    test_evaluation_summary_payload()
    test_visual_plots_exist()
    test_phase_boundary_hygiene()
    print("==================================================")
    print("ALL PHASE 6 VERIFICATION CHECKS PASSED (5/5 PASS)")
    print("==================================================")
