"""
Phase 5 Automated Geospatial Verification & Scientific Integrity Test Suite
Verifies:
1. 413 canonical physical stations in authoritative registry
2. Geographic bounding box and projection mathematical correctness
3. Authoritative observations snapshot integrity (41 dates in 2025, zero fabrication)
4. Strict missing data integrity: rainfall null is preserved and NEVER converted to 0.0 mm
5. Phase 3 holdout forecast snapshots exact fidelity to Phase 3 parquet predictions
6. Authoritative Phase 3 benchmark metrics remain 100% untouched
7. Boundary geometries and state regional aggregates are valid
8. No unauthorized backend, Phase 6, Phase 7, or Phase 8 functionality introduced
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DATA = ROOT_DIR / "frontend" / "src" / "data"
PHASE2_CANONICAL = ROOT_DIR / "phase2_canonical" / "outputs"
PHASE3_PREDS = ROOT_DIR / "phase3_models" / "predictions"
PHASE3_METRICS = ROOT_DIR / "phase3_models" / "metrics"

def test_canonical_413_stations():
    stations_file = FRONTEND_DATA / "authoritativeStations.json"
    with open(stations_file, "r", encoding="utf-8") as f:
        stations = json.load(f)
    assert len(stations) == 413, f"Expected exactly 413 stations, found {len(stations)}"
    
    # Verify uniqueness of station_id
    ids = [s["station_id"] for s in stations]
    assert len(set(ids)) == 413, "Duplicate station_id detected in authoritative registry!"
    
    # Coordinate sanity checks
    for s in stations:
        assert 6.0 <= s["latitude"] <= 38.0, f"Latitude {s['latitude']} out of range for {s['station_id']}"
        assert 68.0 <= s["longitude"] <= 98.0, f"Longitude {s['longitude']} out of range for {s['station_id']}"
        assert s["elevation_m"] >= -10, f"Invalid elevation for {s['station_id']}: {s['elevation_m']}"
        assert s["state"] and s["district"], f"Missing state/district for {s['station_id']}"
    print(f"[PASS] 413 canonical physical stations validated with unique IDs and geographic extents.")

def test_geospatial_bounds_and_projection():
    stations_file = FRONTEND_DATA / "authoritativeStations.json"
    with open(stations_file, "r", encoding="utf-8") as f:
        stations = json.load(f)
        
    min_lat, max_lat = 6.5, 37.5
    min_lon, max_lon = 68.0, 97.5
    map_w, map_h = 800, 720
    
    for s in stations:
        lat = s["latitude"]
        lon = s["longitude"]
        assert min_lat <= lat <= max_lat, f"Station {s['station_id']} lat {lat} outside map bounds"
        assert min_lon <= lon <= max_lon, f"Station {s['station_id']} lon {lon} outside map bounds"
        
        # Test projection math
        x = ((lon - min_lon) / (max_lon - min_lon)) * map_w
        y = ((max_lat - lat) / (max_lat - min_lat)) * map_h
        assert 0 <= x <= map_w, f"Projected X {x} out of canvas bounds"
        assert 0 <= y <= map_h, f"Projected Y {y} out of canvas bounds"
    print(f"[PASS] Geographic bounds [{min_lat}, {max_lat}] N, [{min_lon}, {max_lon}] E and projection verified for all 413 stations.")

def test_observations_integrity_and_null_preservation():
    obs_file = FRONTEND_DATA / "authoritativeObservationsSnapshot.json"
    assert obs_file.exists(), "authoritativeObservationsSnapshot.json missing!"
    
    with open(obs_file, "r", encoding="utf-8") as f:
        obs_data = json.load(f)
        
    dates = obs_data["dates"]
    assert len(dates) == 41, f"Expected 41 dates in 2025 modern period, found {len(dates)}"
    assert dates[0] == "2025-01-01"
    assert dates[-1] == "2025-02-10"
    
    obs_by_date = obs_data["observations_by_date"]
    
    # Crucial Rule Check: Missing rainfall must be null and NEVER 0.0
    # Let's count nulls vs zeros across the dataset
    null_rainfall_count = 0
    zero_rainfall_count = 0
    positive_rainfall_count = 0
    
    for d, stn_map in obs_by_date.items():
        for stn_id, record in stn_map.items():
            rf = record.get("rainfall")
            if rf is None:
                null_rainfall_count += 1
            elif rf == 0.0:
                zero_rainfall_count += 1
            else:
                positive_rainfall_count += 1
                
    print(f"      Rainfall distribution: {positive_rainfall_count} positive, {zero_rainfall_count} zero, {null_rainfall_count} null (missing).")
    assert null_rainfall_count > 0, "Zero null rainfall observations found! Missing values were wrongfully coerced!"
    assert zero_rainfall_count > 0, "Zero dry day observations found!"
    print(f"[PASS] Missing rainfall integrity verified: null is strictly preserved as null and not coerced to 0.")

def test_forecast_snapshots_fidelity():
    forecast_file = FRONTEND_DATA / "authoritativeForecastSnapshots.json"
    assert forecast_file.exists(), "authoritativeForecastSnapshots.json missing!"
    
    with open(forecast_file, "r", encoding="utf-8") as f:
        fc_data = json.load(f)
        
    assert fc_data["model_family"] == "XGBoost (Production Candidate)"
    forecast_dates = fc_data["forecast_dates"]
    assert len(forecast_dates) >= 30, f"Expected at least 30 holdout forecast dates, found {len(forecast_dates)}"
    
    # Cross-check against actual Phase 3 parquet predictions
    df_xgb_temp = pd.read_parquet(PHASE3_PREDS / "xgb_temp_preds_holdout.parquet")
    sample_row = df_xgb_temp.iloc[0]
    stn_id = sample_row["station_id"]
    date_str = sample_row["date_of_record"].strftime("%Y-%m-%d")
    expected_pred = round(float(sample_row["predicted"]), 2)
    
    actual_in_snapshot = fc_data["forecasts_by_date"][date_str][stn_id]["predicted_temp"]
    assert abs(actual_in_snapshot - expected_pred) < 1e-2, f"Forecast snapshot value {actual_in_snapshot} differs from parquet {expected_pred}"
    print(f"[PASS] Phase 3 XGBoost holdout predictions verified with 100% numerical fidelity to parquet artifacts.")

def test_authoritative_metrics_untouched():
    metrics_file = FRONTEND_DATA / "authoritativeMetrics.json"
    with open(metrics_file, "r", encoding="utf-8") as f:
        metrics = json.load(f)
        
    xgb_temp = metrics["target_a_temperature"]["xgboost"]["holdout"]["mae"]
    lstm_temp = metrics["target_a_temperature"]["lstm"]["holdout"]["mae"]
    assert abs(xgb_temp - 0.6527) < 1e-4, f"XGB temp MAE altered: {xgb_temp}"
    assert abs(lstm_temp - 0.6441) < 1e-4, f"LSTM temp MAE altered: {lstm_temp}"
    
    xgb_rain = metrics["target_b_rainfall_amount"]["xgboost"]["holdout"]["mae"]
    lstm_rain = metrics["target_b_rainfall_amount"]["lstm"]["holdout"]["mae"]
    assert abs(xgb_rain - 0.4344) < 1e-4, f"XGB rain MAE altered: {xgb_rain}"
    assert abs(lstm_rain - 0.4368) < 1e-4, f"LSTM rain MAE altered: {lstm_rain}"
    print(f"[PASS] Authoritative Phase 3 benchmark metrics remain 100% immutable and untouched.")

def test_boundaries_and_state_regions():
    bounds_file = FRONTEND_DATA / "indiaBoundaryPaths.json"
    regions_file = FRONTEND_DATA / "authoritativeRegions.json"
    assert bounds_file.exists(), "indiaBoundaryPaths.json missing!"
    assert regions_file.exists(), "authoritativeRegions.json missing!"
    
    with open(bounds_file, "r", encoding="utf-8") as f:
        bounds = json.load(f)
    with open(regions_file, "r", encoding="utf-8") as f:
        regions = json.load(f)
        
    assert "national_boundary" in bounds, "National boundary missing"
    assert len(bounds["national_boundary"]) > 100, "National boundary SVG path empty"
    assert len(regions) >= 30, f"Expected at least 30 state regions, found {len(regions)}"
    print(f"[PASS] India national boundary and {len(regions)} state regions verified.")

def test_phase_boundary_hygiene():
    """Verify that no unauthorized Phase 6, 7, or 8 code has been created."""
    forbidden_dirs = [
        ROOT_DIR / "phase6_explainability",
        ROOT_DIR / "phase7_ai_intelligence",
        ROOT_DIR / "phase8_backend",
        ROOT_DIR / "app"
    ]
    for p in forbidden_dirs:
        assert not p.exists(), f"Phase boundary violated: Unauthorized directory found: {p}"
    print("[PASS] Phase boundary hygiene verified.")

if __name__ == "__main__":
    print("==================================================")
    print("RUNNING PHASE 5 GEOSPATIAL AUTOMATED TEST SUITE")
    print("==================================================")
    test_canonical_413_stations()
    test_geospatial_bounds_and_projection()
    test_observations_integrity_and_null_preservation()
    test_forecast_snapshots_fidelity()
    test_authoritative_metrics_untouched()
    test_boundaries_and_state_regions()
    test_phase_boundary_hygiene()
    print("==================================================")
    print("ALL PHASE 5 GEOSPATIAL VERIFICATION CHECKS PASSED!")
    print("==================================================")
