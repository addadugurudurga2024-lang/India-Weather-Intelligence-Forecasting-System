"""
Phase 7 Post-Audit Script: Test Real XGBoost Model Inference on Station Feature Vector
"""
import json
import xgboost as xgb
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path("d:/weather_forcasting")
DATA_PATH = ROOT / "phase2_canonical" / "outputs" / "features_engineered.parquet"
MODELS_DIR = ROOT / "phase7_forecasting" / "models"

BASE_FEATURES = [
    "avg_temp_clean", "min_temp_clean", "max_temp_clean",
    "wind_speed", "air_pressure", "rainfall",
    "elevation", "latitude", "longitude",
    "lag_1_avg_temp", "lag_2_avg_temp", "lag_1_min_temp", "lag_1_max_temp",
    "lag_1_rainfall", "lag_2_rainfall", "lag_1_wind_speed", "lag_1_air_pressure",
    "rolling_3d_temp_mean", "rolling_7d_temp_mean", "rolling_7d_temp_std",
    "rolling_3d_rainfall_sum", "rolling_7d_rainfall_sum",
]

def test_inference_for_station(station_id="new_delhi_safdarjung_28.5833_77.2000_211m", date_str="2025-01-20"):
    df = pd.read_parquet(DATA_PATH)
    df["date_of_record"] = pd.to_datetime(df["date_of_record"])
    row = df[(df["station_id"] == station_id) & (df["date_of_record"] == date_str)]
    
    if row.empty:
        print(f"No row found for {station_id} on {date_str}")
        return

    features = row[BASE_FEATURES].copy()
    print(f"Station: {station_id} on {date_str}")
    print(f"Observed: AvgTemp={row['avg_temp_clean'].values[0]}°C, Rain={row['rainfall'].values[0]}mm, Wind={row['wind_speed'].values[0]}km/h, Pres={row['air_pressure'].values[0]}hPa")
    
    # Test available models: h=1, 3, 7, 12
    for h in [1, 3, 7, 12]:
        temp_model = xgb.XGBRegressor()
        temp_model.load_model(str(MODELS_DIR / f"xgb_temp_h{h}.json"))
        
        cls_model = xgb.XGBClassifier()
        cls_model.load_model(str(MODELS_DIR / f"xgb_rain_cls_h{h}.json"))
        
        # Add deterministic calendar harmonic
        fc_dt = pd.to_datetime(date_str) + pd.Timedelta(days=h)
        doy = fc_dt.dayofyear
        X = features.copy()
        X[f"doy_sin_h{h}"] = np.sin(2 * np.pi * doy / 365.25)
        X[f"doy_cos_h{h}"] = np.cos(2 * np.pi * doy / 365.25)
        
        pred_temp = float(temp_model.predict(X)[0])
        pred_prob = float(cls_model.predict_proba(X)[0, 1])
        print(f"Horizon T+{h} ({fc_dt.strftime('%Y-%m-%d')}): Model Temp={pred_temp:.2f}°C, Model RainProb={pred_prob*100:.1f}%")

if __name__ == "__main__":
    test_inference_for_station()
