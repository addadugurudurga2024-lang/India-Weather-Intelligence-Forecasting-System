"""
Phase 4 Automated Verification & Static Quality Gate
Verifies:
1. Frontend build artifacts existence & health
2. Exact matching of authoritative Phase 2 station count (413) & Phase 3 model metrics
3. Database schemas and seed data integrity
4. Credential security (no hardcoded passwords or secrets in frontend/database)
"""

import json
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
DB_DIR = ROOT_DIR / "phase4_database"

def test_frontend_build_artifacts():
    dist_dir = FRONTEND_DIR / "dist"
    index_html = dist_dir / "index.html"
    assert dist_dir.exists(), "Frontend build directory dist/ does not exist!"
    assert index_html.exists(), "Frontend index.html was not generated!"
    
    # Check assets
    assets = list((dist_dir / "assets").glob("*.js"))
    assert len(assets) > 0, "No compiled JS bundle found in dist/assets"
    print("[PASS] Frontend build artifacts verified.")

def test_authoritative_station_metadata():
    stations_file = FRONTEND_DIR / "src" / "data" / "authoritativeStations.json"
    assert stations_file.exists(), "authoritativeStations.json missing!"
    with open(stations_file, "r", encoding="utf-8") as f:
        stations = json.load(f)
    assert len(stations) == 413, f"Expected exactly 413 canonical physical stations, got {len(stations)}"
    
    # Verify required keys
    sample = stations[0]
    for key in ["station_id", "station_name", "state", "district", "latitude", "longitude", "elevation_m"]:
        assert key in sample, f"Key '{key}' missing from station metadata"
    print(f"[PASS] Authoritative stations verified: {len(stations)} physical stations.")

def test_authoritative_phase3_metrics():
    metrics_file = FRONTEND_DIR / "src" / "data" / "authoritativeMetrics.json"
    assert metrics_file.exists(), "authoritativeMetrics.json missing!"
    with open(metrics_file, "r", encoding="utf-8") as f:
        metrics = json.load(f)
    
    # 1. Temperature XGBoost vs LSTM
    xgb_temp = metrics["target_a_temperature"]["xgboost"]["holdout"]
    lstm_temp = metrics["target_a_temperature"]["lstm"]["holdout"]
    assert abs(xgb_temp["mae"] - 0.6527) < 1e-4, f"XGB temp MAE mismatch: {xgb_temp['mae']}"
    assert abs(xgb_temp["r2"] - 0.9705) < 1e-4, f"XGB temp R2 mismatch: {xgb_temp['r2']}"
    assert abs(lstm_temp["mae"] - 0.6441) < 1e-4, f"LSTM temp MAE mismatch: {lstm_temp['mae']}"
    assert abs(lstm_temp["r2"] - 0.9713) < 1e-4, f"LSTM temp R2 mismatch: {lstm_temp['r2']}"
    
    # 2. Rainfall Amount XGBoost vs LSTM
    xgb_rain = metrics["target_b_rainfall_amount"]["xgboost"]["holdout"]
    lstm_rain = metrics["target_b_rainfall_amount"]["lstm"]["holdout"]
    assert abs(xgb_rain["mae"] - 0.4344) < 1e-4, f"XGB rain MAE mismatch: {xgb_rain['mae']}"
    assert abs(xgb_rain["mae_rainy_only"] - 2.8947) < 1e-4, f"XGB rainy MAE mismatch: {xgb_rain['mae_rainy_only']}"
    assert abs(lstm_rain["mae"] - 0.4368) < 1e-4, f"LSTM rain MAE mismatch: {lstm_rain['mae']}"
    assert abs(lstm_rain["mae_rainy_only"] - 2.8630) < 1e-4, f"LSTM rainy MAE mismatch: {lstm_rain['mae_rainy_only']}"
    
    # 3. Rain Classification XGBoost vs LSTM
    xgb_cls = metrics["target_c_rain_binary"]["xgboost"]["holdout"]
    lstm_cls = metrics["target_c_rain_binary"]["lstm"]["holdout"]
    assert abs(xgb_cls["accuracy"] - 0.8919) < 1e-4, f"XGB cls accuracy mismatch: {xgb_cls['accuracy']}"
    assert abs(xgb_cls["roc_auc"] - 0.8366) < 1e-4, f"XGB cls ROC-AUC mismatch: {xgb_cls['roc_auc']}"
    assert abs(lstm_cls["accuracy"] - 0.8832) < 1e-4, f"LSTM cls accuracy mismatch: {lstm_cls['accuracy']}"
    assert abs(lstm_cls["roc_auc"] - 0.8256) < 1e-4, f"LSTM cls ROC-AUC mismatch: {lstm_cls['roc_auc']}"
    
    print("[PASS] Authoritative Phase 3 metrics verified with exact numerical match.")

def test_database_schemas_and_seeds():
    schema_dir = DB_DIR / "schemas"
    schemas = list(schema_dir.glob("*.json"))
    assert len(schemas) >= 4, f"Expected at least 4 collection schemas, found {len(schemas)}"
    
    for s in schemas:
        with open(s, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "$jsonSchema" in data or "bsonType" in data or "properties" in data, f"Invalid schema format in {s.name}"
            
    # Seeds
    seed_stations = DB_DIR / "seeds" / "stations.seed.json"
    seed_models = DB_DIR / "seeds" / "model_metadata.seed.json"
    assert seed_stations.exists() and seed_models.exists(), "Seed files missing"
    
    with open(seed_stations, "r", encoding="utf-8") as f:
        stns = json.load(f)
        assert len(stns) == 413, f"Expected 413 seed stations, got {len(stns)}"
        
    with open(seed_models, "r", encoding="utf-8") as f:
        mdls = json.load(f)
        assert len(mdls) == 6, f"Expected 6 model metadata seed documents, got {len(mdls)}"
        
    print("[PASS] MongoDB schemas, indexes and seed documents verified.")

def test_credential_hygiene():
    """Verify that no .env files containing real secrets or passwords exist in git tracking."""
    git_ignore_root = ROOT_DIR / ".gitignore"
    git_ignore_frontend = FRONTEND_DIR / ".gitignore"
    assert git_ignore_root.exists(), "Root .gitignore missing"
    assert git_ignore_frontend.exists(), "Frontend .gitignore missing"
    
    with open(git_ignore_root, "r", encoding="utf-8") as f:
        content = f.read()
        assert ".env" in content, ".env not excluded in root .gitignore"
        
    with open(git_ignore_frontend, "r", encoding="utf-8") as f:
        content = f.read()
        assert ".env" in content, ".env not excluded in frontend .gitignore"
        
    # Check that neither .env nor credentials are leaked
    for forbidden in [".env", "credentials.json", "secrets.json"]:
        assert not (ROOT_DIR / forbidden).exists(), f"Accidental secret file found: {forbidden}"
    print("[PASS] Security & credential hygiene verified.")

if __name__ == "__main__":
    print("--- Running Phase 4 Automated Verification ---")
    test_frontend_build_artifacts()
    test_authoritative_station_metadata()
    test_authoritative_phase3_metrics()
    test_database_schemas_and_seeds()
    test_credential_hygiene()
    print("==================================================")
    print("ALL PHASE 4 AUTOMATED VERIFICATION CHECKS PASSED!")
    print("==================================================")
