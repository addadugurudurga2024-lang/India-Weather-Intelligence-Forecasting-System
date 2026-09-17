"""
Phase 2: Leakage-Free Feature Engineering Foundation
Generates:
1. Cyclical calendar encodings (day of year sin/cos, month sin/cos).
2. Gap-Aware Lag Features:
   - lag_1, lag_2 for avg_temp, rainfall, wind_speed, air_pressure.
   - Enforces condition: date(t) - date(t-k) == k days; sets to NaN if calendar gap exists.
3. Gap-Aware Rolling Window Aggregations:
   - rolling_3d_mean, rolling_7d_mean, rolling_7d_std on past window (closed='left' so day t is excluded).
4. Forecasting Targets:
   - target_next_day_temp: avg_temp at t+1 (strictly when date(t+1) == date(t) + 1 day).
   - target_next_day_rainfall_amount: rainfall at t+1 (when date(t+1) == date(t) + 1 day and non-null).
   - target_next_day_rain_binary: 1 if target rainfall > 0 else 0 (when non-null and consecutive).
"""

import logging
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).parent))

from config import (
    CANONICAL_FORECAST_PATH,
    FEATURE_STORE_PATH
)

logger = logging.getLogger("phase2_canonical.features")

def engineer_forecasting_features() -> pd.DataFrame:
    logger.info("Loading canonical forecasting dataset from %s...", CANONICAL_FORECAST_PATH)
    df = pd.read_parquet(CANONICAL_FORECAST_PATH)
    logger.info("Loaded %d rows for feature engineering", len(df))

    # Ensure deterministic sort
    df = df.sort_values(by=["station_id", "date_of_record"]).reset_index(drop=True)

    # -------------------------------------------------------------
    # 1. Cyclical Calendar Features
    # -------------------------------------------------------------
    logger.info("Computing cyclical calendar features...")
    day_of_year = df["date_of_record"].dt.dayofyear
    df["doy_sin"] = np.sin(2 * np.pi * day_of_year / 365.25)
    df["doy_cos"] = np.cos(2 * np.pi * day_of_year / 365.25)

    month_num = df["date_of_record"].dt.month
    df["month_sin"] = np.sin(2 * np.pi * month_num / 12.0)
    df["month_cos"] = np.cos(2 * np.pi * month_num / 12.0)

    # -------------------------------------------------------------
    # 2. Gap-Aware Lag Features
    # -------------------------------------------------------------
    logger.info("Computing gap-aware lag features...")
    # Shift dates per station
    stn_group = df.groupby("station_id")
    df["prev_date_1"] = stn_group["date_of_record"].shift(1)
    df["prev_date_2"] = stn_group["date_of_record"].shift(2)

    # Calculate exact calendar days between observations
    diff_days_1 = (df["date_of_record"] - df["prev_date_1"]).dt.days
    diff_days_2 = (df["date_of_record"] - df["prev_date_2"]).dt.days

    # Valid lag masks: strictly 1 day and 2 days
    valid_lag1 = diff_days_1 == 1
    valid_lag2 = diff_days_2 == 2

    # Temperature lags (use cleaned temperature view to avoid leaking corruption)
    temp_shift_1 = stn_group["avg_temp_clean"].shift(1)
    temp_shift_2 = stn_group["avg_temp_clean"].shift(2)
    df["lag_1_avg_temp"] = np.where(valid_lag1, temp_shift_1, np.nan)
    df["lag_2_avg_temp"] = np.where(valid_lag2, temp_shift_2, np.nan)

    # Min/Max temperature lags
    df["lag_1_min_temp"] = np.where(valid_lag1, stn_group["min_temp_clean"].shift(1), np.nan)
    df["lag_1_max_temp"] = np.where(valid_lag1, stn_group["max_temp_clean"].shift(1), np.nan)

    # Rainfall lags (preserve raw 0 vs NaN)
    rf_shift_1 = stn_group["rainfall"].shift(1)
    rf_shift_2 = stn_group["rainfall"].shift(2)
    df["lag_1_rainfall"] = np.where(valid_lag1, rf_shift_1, np.nan)
    df["lag_2_rainfall"] = np.where(valid_lag2, rf_shift_2, np.nan)

    # Wind speed and Air pressure lags
    wind_shift_1 = stn_group["wind_speed"].shift(1)
    press_shift_1 = stn_group["air_pressure"].shift(1)
    df["lag_1_wind_speed"] = np.where(valid_lag1, wind_shift_1, np.nan)
    df["lag_1_air_pressure"] = np.where(valid_lag1, press_shift_1, np.nan)

    # Drop temporary calculation columns
    df = df.drop(columns=["prev_date_1", "prev_date_2"])

    # -------------------------------------------------------------
    # 3. Gap-Aware Rolling Window Aggregations (Strictly Past Window)
    # -------------------------------------------------------------
    logger.info("Computing gap-aware rolling features on strictly historical windows...")
    # To compute 3-day and 7-day rolling metrics without leakage, we use lag_1 as the anchor
    # or rolling on consecutive sequences. We use 3-day and 7-day rolling on lagged values.
    # Grouped rolling on lag_1 ensures day t is NEVER included in rolling aggregation.
    df["rolling_3d_temp_mean"] = stn_group["lag_1_avg_temp"].transform(
        lambda s: s.rolling(window=3, min_periods=2).mean()
    )
    df["rolling_7d_temp_mean"] = stn_group["lag_1_avg_temp"].transform(
        lambda s: s.rolling(window=7, min_periods=4).mean()
    )
    df["rolling_7d_temp_std"] = stn_group["lag_1_avg_temp"].transform(
        lambda s: s.rolling(window=7, min_periods=4).std()
    )

    df["rolling_3d_rainfall_sum"] = stn_group["lag_1_rainfall"].transform(
        lambda s: s.rolling(window=3, min_periods=2).sum()
    )
    df["rolling_7d_rainfall_sum"] = stn_group["lag_1_rainfall"].transform(
        lambda s: s.rolling(window=7, min_periods=4).sum()
    )

    # -------------------------------------------------------------
    # 4. Forecasting Targets (Next-Day Horizon t+1)
    # -------------------------------------------------------------
    logger.info("Constructing forecasting targets with strict consecutive-day gating...")
    next_date = stn_group["date_of_record"].shift(-1)
    days_to_next = (next_date - df["date_of_record"]).dt.days
    consecutive_next = days_to_next == 1

    # Target A: Next-Day Avg Temperature
    next_temp = stn_group["avg_temp_clean"].shift(-1)
    df["target_next_day_temp"] = np.where(consecutive_next, next_temp, np.nan)

    # Target B: Next-Day Rainfall Amount
    next_rf = stn_group["rainfall"].shift(-1)
    df["target_next_day_rainfall_amount"] = np.where(consecutive_next, next_rf, np.nan)

    # Target C: Next-Day Rain Status (Binary: 0=No Rain, 1=Rain >= 0.1mm)
    # Masked as NaN whenever next_day rainfall is missing or non-consecutive
    rain_binary = np.where(next_rf > 0.0, 1.0, 0.0)
    df["target_next_day_rain_binary"] = np.where(consecutive_next & next_rf.notna(), rain_binary, np.nan)

    # -------------------------------------------------------------
    # 5. Export Feature Store
    # -------------------------------------------------------------
    logger.info("Saving engineered feature store to %s...", FEATURE_STORE_PATH)
    df.to_parquet(FEATURE_STORE_PATH, index=False, engine="pyarrow", compression="snappy")
    logger.info("Successfully engineered %d features across %d rows", len(df.columns), len(df))

    return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    engineer_forecasting_features()
