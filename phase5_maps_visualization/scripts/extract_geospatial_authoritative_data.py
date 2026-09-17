"""
Phase 5 Geospatial Data Extraction Script
Authoritative, deterministic data extraction from Phase 2 canonical datasets and Phase 3 model holdout predictions.
Zero fabrication: Every single value is extracted from canonical parquet artifacts.
"""

import json
import os
from pathlib import Path
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
CANONICAL_PARQUET = ROOT_DIR / "phase2_canonical" / "outputs" / "canonical_weather_forecasting.parquet"
STATION_METADATA = ROOT_DIR / "phase2_canonical" / "outputs" / "station_metadata.json"
PRED_DIR = ROOT_DIR / "phase3_models" / "predictions"
FRONTEND_DATA_DIR = ROOT_DIR / "frontend" / "src" / "data"

def extract_authoritative_geospatial_data():
    print("--- Starting Phase 5 Authoritative Geospatial Data Extraction ---")
    
    # 1. Load Station Metadata (413 stations)
    with open(STATION_METADATA, "r", encoding="utf-8") as f:
        data = json.load(f)
        stations = list(data.values()) if isinstance(data, dict) else data
    print(f"Loaded {len(stations)} canonical stations.")
    station_dict = {s["station_id"]: s for s in stations}
    
    # 2. Extract 2025 Daily Observations from canonical parquet
    print(f"Reading {CANONICAL_PARQUET}...")
    df_obs = pd.read_parquet(
        CANONICAL_PARQUET,
        columns=[
            "date_of_record", "station_id", "station_name", "state", "district",
            "avg_temp", "min_temp", "max_temp", "rainfall", "wind_speed", "air_pressure"
        ]
    )
    
    # Filter 2025 modern period (2025-01-01 to 2025-02-10)
    df_2025 = df_obs[df_obs["date_of_record"] >= "2025-01-01"].copy()
    df_2025["date_str"] = df_2025["date_of_record"].dt.strftime("%Y-%m-%d")
    
    unique_dates = sorted(df_2025["date_str"].unique())
    print(f"Found {len(unique_dates)} dates in 2025: {unique_dates[0]} to {unique_dates[-1]}")
    print(f"Total observation rows: {len(df_2025)}")
    
    # Structure observations by date -> station_id for instant O(1) lookup in frontend
    # Strict preservation: If a station did not report or has NaN, it is stored as None (never coerced to 0)
    obs_by_date = {}
    
    # Map (date, station_id) -> row
    row_map = {}
    for _, row in df_2025.iterrows():
        row_map[(row["date_str"], row["station_id"])] = row

    for d in unique_dates:
        obs_by_date[d] = {}
        for stn_id in station_dict.keys():
            key = (d, stn_id)
            if key in row_map:
                row = row_map[key]
                rainfall_val = None if pd.isna(row["rainfall"]) else round(float(row["rainfall"]), 2)
                avg_temp_val = None if pd.isna(row["avg_temp"]) else round(float(row["avg_temp"]), 2)
                min_temp_val = None if pd.isna(row["min_temp"]) else round(float(row["min_temp"]), 2)
                max_temp_val = None if pd.isna(row["max_temp"]) else round(float(row["max_temp"]), 2)
                wind_speed_val = None if pd.isna(row["wind_speed"]) else round(float(row["wind_speed"]), 2)
                air_press_val = None if pd.isna(row["air_pressure"]) else round(float(row["air_pressure"]), 2)
                
                obs_by_date[d][stn_id] = {
                    "avg_temp": avg_temp_val,
                    "min_temp": min_temp_val,
                    "max_temp": max_temp_val,
                    "rainfall": rainfall_val,
                    "wind_speed": wind_speed_val,
                    "air_pressure": air_press_val,
                    "is_rainy": (rainfall_val > 0) if (rainfall_val is not None) else None
                }
            else:
                # Non-reporting station on this date: explicit missing data record
                obs_by_date[d][stn_id] = {
                    "avg_temp": None,
                    "min_temp": None,
                    "max_temp": None,
                    "rainfall": None,
                    "wind_speed": None,
                    "air_pressure": None,
                    "is_rainy": None
                }
        
    obs_output_path = FRONTEND_DATA_DIR / "authoritativeObservationsSnapshot.json"
    with open(obs_output_path, "w", encoding="utf-8") as f:
        json.dump({
            "dates": unique_dates,
            "station_count": len(station_dict),
            "observations_by_date": obs_by_date
        }, f)
    print(f"Wrote observations snapshot to {obs_output_path} ({os.path.getsize(obs_output_path) / 1024:.1f} KB)")
    
    # 3. Extract Phase 3 Holdout Forecasts from XGBoost holdout predictions
    xgb_temp_file = PRED_DIR / "xgb_temp_preds_holdout.parquet"
    xgb_rain_file = PRED_DIR / "xgb_rain_preds_holdout.parquet"
    xgb_cls_file = PRED_DIR / "xgb_rain_cls_preds_holdout.parquet"
    
    print("Reading Phase 3 XGBoost holdout predictions...")
    df_pred_temp = pd.read_parquet(xgb_temp_file)
    df_pred_rain = pd.read_parquet(xgb_rain_file)
    df_pred_cls = pd.read_parquet(xgb_cls_file)
    
    df_pred_temp["date_str"] = df_pred_temp["date_of_record"].dt.strftime("%Y-%m-%d")
    df_pred_rain["date_str"] = df_pred_rain["date_of_record"].dt.strftime("%Y-%m-%d")
    df_pred_cls["date_str"] = df_pred_cls["date_of_record"].dt.strftime("%Y-%m-%d")
    
    # Rename columns for clarity before merge
    t_sub = df_pred_temp[["station_id", "date_str", "actual", "predicted"]].rename(
        columns={"actual": "actual_temp", "predicted": "predicted_temp"}
    )
    r_sub = df_pred_rain[["station_id", "date_str", "actual", "predicted"]].rename(
        columns={"actual": "actual_rain", "predicted": "predicted_rain"}
    )
    c_sub = df_pred_cls[["station_id", "date_str", "actual", "predicted", "probability"]].rename(
        columns={"actual": "actual_rain_binary", "predicted": "predicted_rain_binary", "probability": "rain_probability"}
    )
    
    merged_preds = t_sub.merge(r_sub, on=["station_id", "date_str"], how="inner")
    merged_preds = merged_preds.merge(c_sub, on=["station_id", "date_str"], how="inner")
    
    forecast_dates = sorted(merged_preds["date_str"].unique())
    print(f"Merged {len(merged_preds)} holdout forecast records across {len(forecast_dates)} dates.")
    
    forecast_by_date = {}
    for d in forecast_dates:
        forecast_by_date[d] = {}
        
    for _, row in merged_preds.iterrows():
        d_str = row["date_str"]
        stn_id = row["station_id"]
        
        forecast_by_date[d_str][stn_id] = {
            "predicted_temp": round(float(row["predicted_temp"]), 2),
            "predicted_rainfall": max(0.0, round(float(row["predicted_rain"]), 2)),
            "rain_probability": round(float(row["rain_probability"]), 3),
            "predicted_rain_binary": bool(row["predicted_rain_binary"] > 0.5),
            "actual_temp": round(float(row["actual_temp"]), 2) if not pd.isna(row["actual_temp"]) else None,
            "actual_rainfall": round(float(row["actual_rain"]), 2) if not pd.isna(row["actual_rain"]) else None,
            "actual_rain_binary": bool(row["actual_rain_binary"] > 0.5) if not pd.isna(row["actual_rain_binary"]) else None,
            "model": "XGBoost Holdout Candidate"
        }
        
    forecast_output_path = FRONTEND_DATA_DIR / "authoritativeForecastSnapshots.json"
    with open(forecast_output_path, "w", encoding="utf-8") as f:
        json.dump({
            "model_family": "XGBoost (Production Candidate)",
            "benchmark_period": "2025 Holdout Validation",
            "forecast_dates": forecast_dates,
            "forecasts_by_date": forecast_by_date
        }, f)
    print(f"Wrote forecasts snapshot to {forecast_output_path} ({os.path.getsize(forecast_output_path) / 1024:.1f} KB)")
    
    # 4. Extract Geographic Region Aggregates (States & Districts)
    # Derive bounds, centroids, station counts, and average elevations deterministically
    state_groups = {}
    for s in stations:
        st = s["state"]
        if st not in state_groups:
            state_groups[st] = []
        state_groups[st].append(s)
        
    regions = []
    for st, st_stations in sorted(state_groups.items()):
        lats = [s["latitude"] for s in st_stations]
        lons = [s["longitude"] for s in st_stations]
        elevations = [s["elevation_m"] for s in st_stations]
        
        districts = sorted(list(set(s["district"] for s in st_stations)))
        
        regions.append({
            "id": st,
            "name": st,
            "type": "STATE",
            "station_count": len(st_stations),
            "district_count": len(districts),
            "districts": districts,
            "station_ids": [s["station_id"] for s in st_stations],
            "bounds": {
                "minLat": round(min(lats), 4),
                "maxLat": round(max(lats), 4),
                "minLon": round(min(lons), 4),
                "maxLon": round(max(lons), 4)
            },
            "centroid": {
                "lat": round(float(np.mean(lats)), 4),
                "lon": round(float(np.mean(lons)), 4)
            },
            "avg_elevation_m": round(float(np.mean(elevations)), 1)
        })
        
    regions_output_path = FRONTEND_DATA_DIR / "authoritativeRegions.json"
    with open(regions_output_path, "w", encoding="utf-8") as f:
        json.dump(regions, f, indent=2)
    print(f"Wrote {len(regions)} state regions to {regions_output_path}")
    print("==================================================")
    print("PHASE 5 AUTHORITATIVE GEOSPATIAL EXTRACTION COMPLETED SUCCESSFULLY")
    print("==================================================")

if __name__ == "__main__":
    extract_authoritative_geospatial_data()
